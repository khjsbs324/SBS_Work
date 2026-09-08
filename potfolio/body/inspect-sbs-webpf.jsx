#target photoshop

(function () {
    app.displayDialogs = DialogModes.NO;

    var psdFile = new File('C:/khjsbs/Po/\uC6F9/sbs-webpf-20240522.psd');
    var reportFile = new File('C:/khjsbs/Po/\uC601\uC0C1/psd-layers.txt');
    var previousDocument = app.documents.length ? app.activeDocument : null;
    var documentRef = null;
    var openedHere = false;

    for (var i = 0; i < app.documents.length; i++) {
        try {
            if (app.documents[i].fullName.fsName === psdFile.fsName) {
                documentRef = app.documents[i];
                break;
            }
        } catch (ignored) {}
    }

    if (!documentRef) {
        documentRef = app.open(psdFile);
        openedHere = true;
    }

    function clean(value) {
        return String(value).replace(/[|\r\n]/g, ' ');
    }

    function pixels(value) {
        try {
            return Math.round(value.as('px') * 100) / 100;
        } catch (ignored) {
            return '';
        }
    }

    var lines = [];
    lines.push([
        'DOCUMENT',
        clean(documentRef.name),
        pixels(documentRef.width),
        pixels(documentRef.height),
        documentRef.resolution,
        clean(documentRef.mode)
    ].join('|'));
    lines.push('DEPTH|TYPE|NAME|VISIBLE|KIND|LEFT|TOP|RIGHT|BOTTOM');

    function walk(container, depth) {
        for (var index = 0; index < container.layers.length; index++) {
            var layer = container.layers[index];
            var kind = '';
            var bounds = ['', '', '', ''];

            if (layer.typename === 'ArtLayer') {
                try { kind = layer.kind.toString(); } catch (ignoredKind) {}
                try {
                    bounds = [
                        pixels(layer.bounds[0]),
                        pixels(layer.bounds[1]),
                        pixels(layer.bounds[2]),
                        pixels(layer.bounds[3])
                    ];
                } catch (ignoredBounds) {}
            }

            lines.push([
                depth,
                clean(layer.typename),
                clean(layer.name),
                layer.visible,
                clean(kind),
                bounds[0],
                bounds[1],
                bounds[2],
                bounds[3]
            ].join('|'));

            if (layer.typename === 'LayerSet') {
                walk(layer, depth + 1);
            }
        }
    }

    walk(documentRef, 0);

    reportFile.encoding = 'UTF8';
    reportFile.open('w');
    reportFile.write(lines.join('\n'));
    reportFile.close();

    if (openedHere) {
        documentRef.close(SaveOptions.DONOTSAVECHANGES);
    }
    if (previousDocument && app.documents.length) {
        try { app.activeDocument = previousDocument; } catch (ignoredRestore) {}
    }
})();
