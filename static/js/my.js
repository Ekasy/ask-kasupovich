(function () {
    'use strict';

    window.addEventListener('load', function () {
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.getElementsByClassName('needs-validation');

        // Loop over them and prevent submission
        var validation = Array.prototype.filter.call(forms, function (form) {
            form.addEventListener('submit', function (event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);
})();


// ajax like handler
$('.js-vote').click(function(ev) {
    ev.preventDefault();
    var $this = $(this),
        action = $this.data('action'),
        data_id = $this.data('id'),
        content = $this.data('content');

    $.ajax('/vote/', {
        method: 'POST',
        data: {
            action: action,
            pk: data_id,
            content: content,
        }
    }).done(function(data) {
        document.getElementById(content + "-" + data_id).innerHTML = data['rating'];
    });
});


// ajax correct answer handler
$('.js-correct').click(function(ev) {
    ev.preventDefault();
    var $this = $(this),
        data_id = $this.data('id');

    is_correct = document.getElementById('is_correct-' + data_id).checked;

    $.ajax('/correct/', {
        method: 'POST',
        data: {
            pk: data_id,
            is_correct: is_correct,
        }
    }).done(function(data) {
        document.getElementById('is_correct-' + data_id).checked = data['is_correct'];
    });
});
