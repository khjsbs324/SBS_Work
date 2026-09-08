#target photoshop

(function () {
    app.displayDialogs = DialogModes.NO;

    var sourcePsd = new File('C:/khjsbs/Po/\uC6F9/sbs-webpf-20240522.psd');
    var assetRoot = 'C:/khjsbs/Po/\uC601\uC0C1/psd-smart-assets/';
    var outputPsd = new File('C:/khjsbs/Po/\uC601\uC0C1/\uD15C\uBC84\uB9B0\uC988_sbs-webpf_\uD569\uC131.psd');
    var outputPng = new File('C:/khjsbs/Po/\uC601\uC0C1/\uD15C\uBC84\uB9B0\uC988_sbs-webpf_\uD569\uC131.png');
    var outputJpg = new File('C:/khjsbs/Po/\uC601\uC0C1/\uD15C\uBC84\uB9B0\uC988_sbs-webpf_\uD569\uC131.jpg');
    var reportFile = new File('C:/khjsbs/Po/\uC601\uC0C1/psd-composite-report.txt');

    var previousDocument = app.documents.length ? app.activeDocument : null;
    var sourceDocument = null;
    var openedHere = false;

    for (var i = 0; i < app.documents.length; i++) {
        try {
            if (app.documents[i].fullName.fsName === sourcePsd.fsName) {
                sourceDocument = app.documents[i];
                break;
            }
        } catch (ignored) {}
    }

    if (!sourceDocument) {
        sourceDocument = app.open(sourcePsd);
        openedHere = true;
    }

    function group(container, name) {
        return container.layerSets.getByName(name);
    }

    function art(container, name) {
        return container.artLayers.getByName(name);
    }

    function px(value) {
        return Math.round(value.as('px') * 100) / 100;
    }

    function boundsText(layer) {
        return [
            px(layer.bounds[0]),
            px(layer.bounds[1]),
            px(layer.bounds[2]),
            px(layer.bounds[3])
        ].join(',');
    }

    function replaceContents(documentRef, layer, filePath) {
        app.activeDocument = documentRef;
        documentRef.activeLayer = layer;
        var descriptor = new ActionDescriptor();
        descriptor.putPath(charIDToTypeID('null'), new File(filePath));
        executeAction(
            stringIDToTypeID('placedLayerReplaceContents'),
            descriptor,
            DialogModes.NO
        );
    }

    var workingDocument = sourceDocument.duplicate(
        'Tamburins_sbs_webpf_composite',
        false
    );
    app.activeDocument = workingDocument;

    var desktop = group(workingDocument, '\uB370\uC2A4\uD06C\uD1B1');
    var targets = [
        {
            label: 'monitor',
            layer: art(group(desktop, 'Apple IMAC'), 'pc-main'),
            asset: assetRoot + 'monitor.png'
        },
        {
            label: 'laptop',
            layer: art(group(desktop, 'Apple Mac Book Pro'), 'pc-sub2'),
            asset: assetRoot + 'laptop.png'
        },
        {
            label: 'main-browser',
            layer: art(group(group(desktop, 'main'), 'mainview_only'), 'pc-main'),
            asset: assetRoot + 'main-browser.png'
        },
        {
            label: 'lower-left',
            layer: art(group(group(desktop, 'sub'), 'subview_only01'), 'pc-sub1'),
            asset: assetRoot + 'lower-left.png'
        },
        {
            label: 'lower-right',
            layer: art(group(group(desktop, 'sub'), 'subview_only02'), 'pc-sub2'),
            asset: assetRoot + 'lower-right.png'
        }
    ];

    var reportLines = [
        'LABEL|BEFORE_BOUNDS|AFTER_BOUNDS|ASSET'
    ];

    for (var targetIndex = 0; targetIndex < targets.length; targetIndex++) {
        var beforeBounds = boundsText(targets[targetIndex].layer);
        replaceContents(
            workingDocument,
            targets[targetIndex].layer,
            targets[targetIndex].asset
        );
        var afterBounds = boundsText(targets[targetIndex].layer);
        reportLines.push([
            targets[targetIndex].label,
            beforeBounds,
            afterBounds,
            targets[targetIndex].asset
        ].join('|'));
    }

    workingDocument.resizeImage(
        undefined,
        undefined,
        300,
        ResampleMethod.NONE
    );

    var psdOptions = new PhotoshopSaveOptions();
    psdOptions.layers = true;
    psdOptions.embedColorProfile = true;
    psdOptions.maximizeCompatibility = true;
    workingDocument.saveAs(outputPsd, psdOptions, true, Extension.LOWERCASE);

    var pngDocument = workingDocument.duplicate('Tamburins_png_export', false);
    pngDocument.flatten();
    var pngOptions = new PNGSaveOptions();
    pngOptions.compression = 3;
    pngOptions.interlaced = false;
    pngDocument.saveAs(outputPng, pngOptions, true, Extension.LOWERCASE);
    pngDocument.close(SaveOptions.DONOTSAVECHANGES);

    app.activeDocument = workingDocument;
    var jpgDocument = workingDocument.duplicate('Tamburins_jpg_export', false);
    jpgDocument.flatten();
    var jpgOptions = new JPEGSaveOptions();
    jpgOptions.quality = 12;
    jpgOptions.embedColorProfile = true;
    jpgOptions.formatOptions = FormatOptions.STANDARDBASELINE;
    jpgDocument.saveAs(outputJpg, jpgOptions, true, Extension.LOWERCASE);
    jpgDocument.close(SaveOptions.DONOTSAVECHANGES);

    reportLines.push([
        'DOCUMENT',
        px(workingDocument.width),
        px(workingDocument.height),
        workingDocument.resolution,
        workingDocument.layers.length
    ].join('|'));
    reportLines.push('PSD|' + outputPsd.fsName);
    reportLines.push('PNG|' + outputPng.fsName);
    reportLines.push('JPG|' + outputJpg.fsName);

    reportFile.encoding = 'UTF8';
    reportFile.open('w');
    reportFile.write(reportLines.join('\n'));
    reportFile.close();

    workingDocument.close(SaveOptions.DONOTSAVECHANGES);

    if (openedHere) {
        sourceDocument.close(SaveOptions.DONOTSAVECHANGES);
    }
    if (previousDocument && app.documents.length) {
        try { app.activeDocument = previousDocument; } catch (ignoredRestore) {}
    }
})();
