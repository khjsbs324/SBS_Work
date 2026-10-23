import argparse
import json
import sys
import zipfile
from .dates import next_weekday
from .records import initialize, record, status


def main(argv=None):
    parser = argparse.ArgumentParser(description='Agent-led NCS support: local deterministic tools only')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('date')
    p.add_argument('end')
    p = sub.add_parser('init')
    for flag in ('course', 'unit', 'end', 'lcode'):
        p.add_argument('--' + flag, required=True)
    p.add_argument('--action', choices=('prepare', 'register'), default='prepare')
    p.add_argument('--request', default='')
    p.add_argument('--meeting', choices=('ensure', 'skip'), default='ensure')
    for command in ('status', 'build', 'package', 'validate'):
        p = sub.add_parser(command)
        p.add_argument('run')
        if command != 'status':
            p.add_argument('group', choices=('A', 'B', 'C'))
    p = sub.add_parser('record')
    p.add_argument('run')
    p.add_argument('--stage', required=True)
    p.add_argument('--group', choices=('A', 'B', 'C'))
    p.add_argument('--evidence', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'date':
            result = {'unit_end_date': args.end, 'post_date': next_weekday(args.end)}
        elif args.command == 'init':
            result = initialize(args.course, args.unit, args.end, args.lcode, args.action, args.request, args.meeting)
        elif args.command == 'status':
            result = status(args.run)
        elif args.command == 'record':
            result = record(args.run, args.stage, args.evidence, args.group)
        elif args.command == 'build':
            from .render import build_group
            result = build_group(args.run, args.group)
        elif args.command == 'package':
            from .package import package_group
            result = package_group(args.run, args.group)
        else:
            from .validate import validate_group
            result = validate_group(args.run, args.group)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, SyntaxError, zipfile.BadZipFile) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
