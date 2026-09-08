#target photoshop

(function () {
    app.displayDialogs = DialogModes.NO;

    var psdFile = new File('C:/khjsbs/Po/\uC6F9/sbs-webpf-20240522.psd');
    var reportFile = new File('C:/khjsbs/Po/\uC601\uC0C1/smart-object-sizes.txt');
    var previousDocument = app.documents.length ? app.activeDocument : null;
    var parentDocument = null;
    var openedHere = false;

    for (var i = 0; i < app.documents.length; i++) {
        try {
            if (app.documents[i].fullName.fsName === psdFile.fsName) {
                parentDocument = app.documents[i];
                break;
            }
        } catch (ignored) {}
    }

    if (!parentDocument) {
        parentDocument = app.open(psdFile);
        openedHere = true;
    }

    function px(value) {
        return Math.round(value.as('px') * 100) / 100;
    }

    function group(container, name) {
        return container.layerSets.getByName(name);
    }

    function art(container, name) {
        return container.artLayers.getByName(name);
    }

    var desktop = group(parentDocument, '\uB370\uC2A4\uD06C\uD1B1');
    var targets = [
        {
            label: 'monitor',
            layer: art(group(desktop, 'Apple IMAC'), 'pc-main')
        },
        {
            label: 'laptop',
            layer: art(group(desktop, 'Apple Mac Book Pro'), 'pc-sub2')
        },
        {
            label: 'main-browser',
            layer: art(group(group(desktop, 'main'), 'mainview_only'), 'pc-main')
        },
        {
            label: 'lower-left',
            layer: art(group(group(desktop, 'sub'), 'subview_only01'), 'pc-sub1')
        },
        {
            label: 'lower-right',
            layer: art(group(group(desktop, 'sub'), 'subview_only02'), 'pc-sub2')
        }
    ];

    var lines = ['LABEL|SMART_NAME|WIDTH|HEIGHT|RESOLUTION|LAYERS'];

    for (var targetIndex = 0; targetIndex < targets.length; targetIndex++) {
        app.activeDocument = parentDocument;
        parentDocument.activeLayer = targets[targetIndex].layer;
        executeAction(
            stringIDToTypeID('placedLayerEditContents'),
            new ActionDescriptor(),
            DialogModes.NO
        );

        var smartDocument = app.activeDocument;
        lines.push([
            targets[targetIndex].label,
            smartDocument.name,
            px(smartDocument.width),
            px(smartDocument.height),
            smartDocument.resolution,
            smartDocument.layers.length
        ].join('|'));
        smartDocument.close(SaveOptions.DONOTSAVECHANGES);
    }

    reportFile.encoding = 'UTF8';
    reportFile.open('w');
    reportFile.write(lines.join('\n'));
    reportFile.close();

    if (openedHere) {
        parentDocument.close(SaveOptions.DONOTSAVECHANGES);
    }
    if (previousDocument && app.documents.length) {
        try { app.activeDocument = previousDocument; } catch (ignoredRestore) {}
    }
})();
