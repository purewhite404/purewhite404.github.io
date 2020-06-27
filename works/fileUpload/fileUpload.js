var form = document.forms.uploadform

form.uploadfile.addEventListener('change', function(e) {
        var result = e.target.files;

        console.log(result);
})
