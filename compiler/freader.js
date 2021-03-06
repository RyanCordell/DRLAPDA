var reader = new FileReader();

function hasFSCompat () {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        return true;
    } else {
        return false;
    }
}

function handleWeaponLanguage (evt) {
    var read = evt.target.files[0];

    readAsText(read);

    reader.addEventListener('load', function (evt) {
        parseWeaponLanguage(evt.target.result);
    });
}

function handleModHeader (evt) {
    var read = evt.target.files[0];

    readAsText(read);

    reader.addEventListener('load', function (evt) {
        parseHeader(evt.target.result);
    });
}

function handleModLanguage (evt) {
    var read = evt.target.files[0];

    readAsText(read);

    reader.addEventListener('load', function (evt) {
        parseModLanguage(evt.target.result);
    });
}

function handleFile (evt) {
    fileList = [];

    for (var i = 0; i < fileInput.files.length; i++) {
        fileList.push(fileInput.files[i]);
    }
}

function processFile (file) {
    readAsText(file);

    reader.addEventListener('load', function (evt) {
        /** 'Allow' for newlines in JSON */
        data = evt.target.result.replace(/\\n(\r\n|\n|\r)/g, '\\n');
        //data = data.replace(/            (?=[a-zA-Z\[\]])(?!")/gm, '');
        /** NOW actually parse */
        data = JSON.parse(data);
        window.pdaglobals = Object.assign(window.pdaglobals, data);
    });
}

function readAsText (file) {
    /** Reinitialize to handle multiple files. There might be a better way than this though...? */
    reader = new FileReader();

    if (file) {
        reader.readAsText(file, 'UTF-8');
        reader.onprogress = function (evt) {
            if (evt.lengthComputable) {
                var loaded = (evt.loaded / evt.total);

                if (loaded < 1) {
                    console.log('Loaded file in: ' + loaded + 'ms');
                }
            }
        };
        reader.onload = function (evt) {
            var fileString = evt.target.result;

            return fileString;
        };
        reader.onerror = function (evt) {
            if (evt.target.error.name === 'NotReadableError') {
                console.error('File could not be read');
            }
        };
    } else {
        throw err('ERROR: File not found or premature cache purge');
    }
}
