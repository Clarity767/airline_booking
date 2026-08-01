

   document.addEventListener("DOMContentLoaded", function () {


    var alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alertEl) {
        setTimeout(function () {
            if (!document.body.contains(alertEl)) {
                return;
            }
            if (window.bootstrap && bootstrap.Alert) {
                var bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                bsAlert.close();
            } else {
                alertEl.classList.remove("show");
                setTimeout(function () { alertEl.remove(); }, 300);
            }
        }, 5000); 
    });


    var forms = document.querySelectorAll('form[method="post"], form[method="POST"]');
    forms.forEach(function (form) {
        form.addEventListener("submit", function () {
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                submitBtn.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>Обробка...';
            }
        });
    });


    var backToTopBtn = document.createElement("button");
    backToTopBtn.type = "button";
    backToTopBtn.id = "backToTopBtn";
    backToTopBtn.innerHTML = "↑";
    backToTopBtn.setAttribute("aria-label", "Нагору");
    document.body.appendChild(backToTopBtn);

    window.addEventListener("scroll", function () {
        if (window.scrollY > 400) {
            backToTopBtn.classList.add("show");
        } else {
            backToTopBtn.classList.remove("show");
        }
    });

    backToTopBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });


    var tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (window.bootstrap && bootstrap.Tooltip) {
        tooltipTriggerList.forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    }

});