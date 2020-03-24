window.onload = function (e) {
    this.console.info('Parser loaded successfully');
    var fileInput = this.document.getElementsByClassName('file__select')[0];

    if (this.hasFSCompat()) {
        console.info('File APIs fully supported, parser will work');
        fileInput.addEventListener('change', handleFile, false);
        this.fetchJSON();
    } else {
        console.error('The File APIs are not fully supported in this browser, this parser will not work otherwise.');
    }
}

function hasFSCompat () {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        return true;
    } else {
        return false;
    }
}

function handleFile (evt) {
    var file = evt.target.files[0];
    var fileObject = document.getElementsByClassName('file__object')[0];
    var fileContent = document.getElementsByClassName('file__content')[0];

    fileObject.innerHTML = file.name;

    readAsText(file);
    //fileContent.innerHTML = file.;

    //console.log(file);
    console.log(file);
}

function readAsText (file) {
    var reader = new FileReader();

    reader.readAsText(file, 'UTF-8');
    reader.onprogress = function (evt) {
        if (evt.lengthComputable) {
            var loaded = (evt.loaded / evt.total);

            if (loaded < 1) {
                console.log(loaded);
            }
        }
    };
    reader.onload = function (evt) {
        var fileString = evt.target.result;

        var JSONObject = JSON.parse(fileString);

        console.log(JSONObject);
    };
    reader.onerror = function (evt) {
        if (evt.target.error.name === 'NotReadableError') {
            console.error('File could not be read');
        }
    };
}

function fetchJSON () {
    // Grab JSON file from current directory
    console.info('JSON loaded');
}