"use strict";

/* =========================================================
   MAD_ALEX — DIGITAL AUTOMATION LAB
   MAIN JAVASCRIPT
========================================================= */


/* =========================================================
   DOM READY
========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initPageLoader();
    initHeader();
    initMobileMenu();
    initSmoothScroll();
    initRevealAnimations();
    initActiveNavigation();
    initCustomCursor();
    initCounters();
    initTiltCards();
    initParticles();
    initPortfolioSlider();
    initProjectModal();
    initSuccessModal();
    initContactForm();
    initPremiumHeroEffects();
});


/* =========================================================
   PAGE LOADER
========================================================= */

function initPageLoader() {
    const loader = document.getElementById("pageLoader");

    if (!loader) {
        return;
    }

    window.addEventListener("load", () => {
        setTimeout(() => {
            loader.classList.add("is-hidden");

            setTimeout(() => {
                loader.style.display = "none";
            }, 800);
        }, 1300);
    });

    setTimeout(() => {
        loader.classList.add("is-hidden");

        setTimeout(() => {
            loader.style.display = "none";
        }, 800);
    }, 3500);
}


/* =========================================================
   HEADER SCROLL
========================================================= */

function initHeader() {
    const header = document.getElementById("header");

    if (!header) {
        return;
    }

    const updateHeader = () => {
        if (window.scrollY > 30) {
            header.classList.add("is-scrolled");
        } else {
            header.classList.remove("is-scrolled");
        }
    };

    updateHeader();

    window.addEventListener("scroll", updateHeader, {
        passive: true
    });
}


/* =========================================================
   MOBILE MENU
========================================================= */

function initMobileMenu() {
    const menuButton = document.getElementById("menuButton");
    const mobileMenu = document.getElementById("mobileMenu");

    if (!menuButton || !mobileMenu) {
        return;
    }

    const mobileLinks = mobileMenu.querySelectorAll("a");

    const openMenu = () => {
        menuButton.classList.add("is-active");
        mobileMenu.classList.add("is-open");
        document.body.classList.add("menu-open");
        menuButton.setAttribute("aria-label", "Закрыть меню");
    };

    const closeMenu = () => {
        menuButton.classList.remove("is-active");
        mobileMenu.classList.remove("is-open");
        document.body.classList.remove("menu-open");
        menuButton.setAttribute("aria-label", "Открыть меню");
    };

    menuButton.addEventListener("click", () => {
        const isOpen = mobileMenu.classList.contains("is-open");

        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    mobileLinks.forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 1024) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });
}


/* =========================================================
   SMOOTH SCROLL
========================================================= */

function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach((link) => {
        link.addEventListener("click", (event) => {
            const href = link.getAttribute("href");

            if (!href || href === "#") {
                return;
            }

            const target = document.querySelector(href);

            if (!target) {
                return;
            }

            event.preventDefault();

            const header = document.getElementById("header");
            const headerHeight = header ? header.offsetHeight : 0;

            const targetPosition =
                target.getBoundingClientRect().top +
                window.scrollY -
                headerHeight +
                2;

            window.scrollTo({
                top: targetPosition,
                behavior: "smooth"
            });
        });
    });
}


/* =========================================================
   REVEAL ANIMATIONS
========================================================= */

function initRevealAnimations() {
    const elements = document.querySelectorAll(".reveal");

    if (!elements.length) {
        return;
    }

    if (!("IntersectionObserver" in window)) {
        elements.forEach((element) => {
            element.classList.add("is-visible");
        });

        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                const element = entry.target;
                const parent = element.parentElement;

                let delay = 0;

                if (parent) {
                    const siblings = Array.from(
                        parent.querySelectorAll(":scope > .reveal")
                    );

                    const index = siblings.indexOf(element);

                    if (index >= 0) {
                        delay = Math.min(index * 90, 450);
                    }
                }

                setTimeout(() => {
                    element.classList.add("is-visible");
                }, delay);

                observer.unobserve(element);
            });
        },
        {
            threshold: 0.12,
            rootMargin: "0px 0px -40px 0px"
        }
    );

    elements.forEach((element) => {
        observer.observe(element);
    });
}


/* =========================================================
   ACTIVE NAVIGATION
========================================================= */

function initActiveNavigation() {
    const sections = document.querySelectorAll("main section[id]");
    const navLinks = document.querySelectorAll(".nav__link");

    if (!sections.length || !navLinks.length) {
        return;
    }

    const updateNavigation = () => {
        const scrollPosition = window.scrollY + 180;
        let currentSection = "";

        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;

            if (
                scrollPosition >= sectionTop &&
                scrollPosition < sectionTop + sectionHeight
            ) {
                currentSection = section.id;
            }
        });

        navLinks.forEach((link) => {
            link.classList.remove("is-active");

            if (
                link.getAttribute("href") ===
                `#${currentSection}`
            ) {
                link.classList.add("is-active");
            }
        });
    };

    updateNavigation();

    window.addEventListener("scroll", updateNavigation, {
        passive: true
    });
}


/* =========================================================
   CUSTOM CURSOR
========================================================= */

function initCustomCursor() {
    const cursorGlow = document.querySelector(".cursor-glow");
    const cursorDot = document.querySelector(".cursor-dot");

    if (!cursorGlow || !cursorDot) {
        return;
    }

    if (
        window.matchMedia("(pointer: coarse)").matches ||
        window.innerWidth <= 768
    ) {
        cursorGlow.style.display = "none";
        cursorDot.style.display = "none";
        return;
    }

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;

    let glowX = mouseX;
    let glowY = mouseY;

    let dotX = mouseX;
    let dotY = mouseY;

    document.addEventListener("mousemove", (event) => {
        mouseX = event.clientX;
        mouseY = event.clientY;
    });

    const animateCursor = () => {
        dotX += (mouseX - dotX) * 0.4;
        dotY += (mouseY - dotY) * 0.4;

        glowX += (mouseX - glowX) * 0.08;
        glowY += (mouseY - glowY) * 0.08;

        cursorDot.style.left = `${dotX}px`;
        cursorDot.style.top = `${dotY}px`;

        cursorGlow.style.left = `${glowX}px`;
        cursorGlow.style.top = `${glowY}px`;

        requestAnimationFrame(animateCursor);
    };

    animateCursor();

    const interactiveElements = document.querySelectorAll(
        "a, button, input, textarea, select, .tilt-card"
    );

    interactiveElements.forEach((element) => {
        element.addEventListener("mouseenter", () => {
            cursorDot.style.transform =
                "translate(-50%, -50%) scale(2)";
            cursorGlow.style.opacity = "1";
        });

        element.addEventListener("mouseleave", () => {
            cursorDot.style.transform =
                "translate(-50%, -50%) scale(1)";
            cursorGlow.style.opacity = "0.8";
        });
    });

    document.addEventListener("mouseleave", () => {
        cursorDot.style.opacity = "0";
        cursorGlow.style.opacity = "0";
    });

    document.addEventListener("mouseenter", () => {
        cursorDot.style.opacity = "1";
        cursorGlow.style.opacity = "0.8";
    });
}


/* =========================================================
   COUNTERS
========================================================= */

function initCounters() {
    const counters = document.querySelectorAll(".counter");

    if (!counters.length) {
        return;
    }

    const animateCounter = (counter) => {
        const target = Number(counter.dataset.target || 0);
        const suffix = counter.dataset.suffix || "";
        const duration = 1600;

        let startTime = null;

        const updateCounter = (currentTime) => {
            if (!startTime) {
                startTime = currentTime;
            }

            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easedProgress =
                1 - Math.pow(1 - progress, 4);

            const currentValue = Math.floor(
                target * easedProgress
            );

            counter.textContent =
                `${currentValue}${suffix}`;

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent =
                    `${target}${suffix}`;
            }
        };

        requestAnimationFrame(updateCounter);
    };

    if (!("IntersectionObserver" in window)) {
        counters.forEach(animateCounter);
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                animateCounter(entry.target);
                observer.unobserve(entry.target);
            });
        },
        {
            threshold: 0.5
        }
    );

    counters.forEach((counter) => {
        observer.observe(counter);
    });
}


/* =========================================================
   TILT CARDS
========================================================= */

function initTiltCards() {
    const cards = document.querySelectorAll(".tilt-card");

    if (!cards.length) {
        return;
    }

    if (
        window.matchMedia("(pointer: coarse)").matches ||
        window.innerWidth <= 768
    ) {
        return;
    }

    cards.forEach((card) => {
        card.addEventListener("mousemove", (event) => {
            const rect = card.getBoundingClientRect();

            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateY =
                ((mouseX - centerX) / centerX) * 5;

            const rotateX =
                ((centerY - mouseY) / centerY) * 5;

            card.style.transform = `
                perspective(900px)
                rotateX(${rotateX}deg)
                rotateY(${rotateY}deg)
                translateY(-5px)
            `;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = `
                perspective(900px)
                rotateX(0deg)
                rotateY(0deg)
                translateY(0)
            `;
        });
    });
}


/* =========================================================
   PARTICLES
========================================================= */

function initParticles() {
    const canvas = document.getElementById("particlesCanvas");

    if (!canvas) {
        return;
    }

    const context = canvas.getContext("2d");

    if (!context) {
        return;
    }

    const particles = [];
    let animationFrameId = null;
    let width = 0;
    let height = 0;

    const mouse = {
        x: null,
        y: null,
        radius: 130
    };

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;

            this.size =
                Math.random() * 1.7 + 0.3;

            this.speedX =
                (Math.random() - 0.5) * 0.35;

            this.speedY =
                (Math.random() - 0.5) * 0.35;

            this.opacity =
                Math.random() * 0.5 + 0.15;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x < 0 || this.x > width) {
                this.speedX *= -1;
            }

            if (this.y < 0 || this.y > height) {
                this.speedY *= -1;
            }

            if (
                mouse.x !== null &&
                mouse.y !== null
            ) {
                const deltaX = mouse.x - this.x;
                const deltaY = mouse.y - this.y;

                const distance = Math.sqrt(
                    deltaX * deltaX +
                    deltaY * deltaY
                );

                if (
                    distance < mouse.radius &&
                    distance > 0
                ) {
                    const force =
                        (mouse.radius - distance) /
                        mouse.radius;

                    this.x -=
                        (deltaX / distance) *
                        force *
                        0.7;

                    this.y -=
                        (deltaY / distance) *
                        force *
                        0.7;
                }
            }
        }

        draw() {
            context.beginPath();

            context.arc(
                this.x,
                this.y,
                this.size,
                0,
                Math.PI * 2
            );

            context.fillStyle =
                `rgba(0, 234, 255, ${this.opacity})`;

            context.fill();
        }
    }

    const resizeCanvas = () => {
        const rect = canvas.getBoundingClientRect();
        const pixelRatio = Math.min(
            window.devicePixelRatio || 1,
            2
        );

        width = rect.width;
        height = rect.height;

        canvas.width = width * pixelRatio;
        canvas.height = height * pixelRatio;

        context.setTransform(
            pixelRatio,
            0,
            0,
            pixelRatio,
            0,
            0
        );

        createParticles();
    };

    const createParticles = () => {
        particles.length = 0;

        const particleCount = Math.min(
            Math.floor((width * height) / 13000),
            110
        );

        for (let index = 0; index < particleCount; index += 1) {
            particles.push(new Particle());
        }
    };

    const drawConnections = () => {
        for (
            let firstIndex = 0;
            firstIndex < particles.length;
            firstIndex += 1
        ) {
            for (
                let secondIndex = firstIndex + 1;
                secondIndex < particles.length;
                secondIndex += 1
            ) {
                const firstParticle =
                    particles[firstIndex];

                const secondParticle =
                    particles[secondIndex];

                const deltaX =
                    firstParticle.x -
                    secondParticle.x;

                const deltaY =
                    firstParticle.y -
                    secondParticle.y;

                const distance =
                    deltaX * deltaX +
                    deltaY * deltaY;

                if (distance < 10500) {
                    const opacity =
                        1 - distance / 10500;

                    context.beginPath();

                    context.moveTo(
                        firstParticle.x,
                        firstParticle.y
                    );

                    context.lineTo(
                        secondParticle.x,
                        secondParticle.y
                    );

                    context.strokeStyle =
                        `rgba(0, 234, 255, ${
                            opacity * 0.08
                        })`;

                    context.lineWidth = 0.6;
                    context.stroke();
                }
            }
        }
    };

    const animateParticles = () => {
        context.clearRect(0, 0, width, height);

        particles.forEach((particle) => {
            particle.update();
            particle.draw();
        });

        drawConnections();

        animationFrameId =
            requestAnimationFrame(animateParticles);
    };

    canvas.addEventListener("mousemove", (event) => {
        const rect = canvas.getBoundingClientRect();

        mouse.x = event.clientX - rect.left;
        mouse.y = event.clientY - rect.top;
    });

    canvas.addEventListener("mouseleave", () => {
        mouse.x = null;
        mouse.y = null;
    });

    window.addEventListener("resize", () => {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }

        resizeCanvas();
        animateParticles();
    });

    resizeCanvas();
    animateParticles();
}


/* =========================================================
   PORTFOLIO SLIDER
========================================================= */

function initPortfolioSlider() {
    const track = document.getElementById("portfolioTrack");
    const previousButton =
        document.getElementById("portfolioPrev");
    const nextButton =
        document.getElementById("portfolioNext");
    const currentElement =
        document.getElementById("portfolioCurrent");
    const progressElement =
        document.getElementById("portfolioProgress");

    if (
        !track ||
        !previousButton ||
        !nextButton
    ) {
        return;
    }

    const slides = track.querySelectorAll(".project-card");

    if (!slides.length) {
        return;
    }

    let currentIndex = 0;
    let startX = 0;
    let endX = 0;

    const formatNumber = (number) => {
        return String(number).padStart(2, "0");
    };

    const updateSlider = () => {
        track.style.transform =
            `translateX(-${currentIndex * 100}%)`;

        if (currentElement) {
            currentElement.textContent =
                formatNumber(currentIndex + 1);
        }

        if (progressElement) {
            const progress =
                ((currentIndex + 1) / slides.length) *
                100;

            progressElement.style.width =
                `${progress}%`;
        }
    };

    const showNextSlide = () => {
        currentIndex += 1;

        if (currentIndex >= slides.length) {
            currentIndex = 0;
        }

        updateSlider();
    };

    const showPreviousSlide = () => {
        currentIndex -= 1;

        if (currentIndex < 0) {
            currentIndex = slides.length - 1;
        }

        updateSlider();
    };

    nextButton.addEventListener("click", showNextSlide);
    previousButton.addEventListener(
        "click",
        showPreviousSlide
    );

    track.addEventListener(
        "touchstart",
        (event) => {
            startX = event.touches[0].clientX;
        },
        {
            passive: true
        }
    );

    track.addEventListener(
        "touchend",
        (event) => {
            endX = event.changedTouches[0].clientX;

            const difference = startX - endX;

            if (Math.abs(difference) < 50) {
                return;
            }

            if (difference > 0) {
                showNextSlide();
            } else {
                showPreviousSlide();
            }
        },
        {
            passive: true
        }
    );

    document.addEventListener("keydown", (event) => {
        const portfolioSection =
            document.getElementById("portfolio");

        if (!portfolioSection) {
            return;
        }

        const rect =
            portfolioSection.getBoundingClientRect();

        const isVisible =
            rect.top < window.innerHeight &&
            rect.bottom > 0;

        if (!isVisible) {
            return;
        }

        if (event.key === "ArrowRight") {
            showNextSlide();
        }

        if (event.key === "ArrowLeft") {
            showPreviousSlide();
        }
    });

    updateSlider();
}


/* =========================================================
   PROJECT MODAL
========================================================= */

function initProjectModal() {
    const modal = document.getElementById("projectModal");

    if (!modal) {
        return;
    }

    const openButtons =
        document.querySelectorAll(".open-project-modal");

    const closeButtons =
        modal.querySelectorAll("[data-close-modal]");

    const modalIndex =
        document.getElementById("modalIndex");

    const modalTitle =
        document.getElementById("modalTitle");

    const modalDescription =
        document.getElementById("modalDescription");

    const modalFeatures =
        document.getElementById("modalFeatures");

    const modalTags =
        document.getElementById("modalTags");

    const projects = {
        booking: {
            index: "WORKING PROTOTYPE / 01",
            title: "Game Club Booking Bot",
            description:
                "Telegram-бот для бронирования игровых компьютеров. Клиент регистрируется, выбирает обычный или VIP-зал, конкретное место, длительность, дату и время. Бот проверяет выбранный слот, сохраняет бронь и сразу уведомляет администратора.",
            features: [
                "Регистрация клиента по имени и номеру телефона",
                "Выбор общего зала на 20 ПК или VIP-зала на 5 мест",
                "Выбор компьютера, длительности, даты и времени",
                "Проверка занятости выбранного слота",
                "Хранение пользователей и броней в SQLite",
                "Мгновенное уведомление администратора",
                "Админ-панель со списком и удалением броней",
                "Разделы с прайсом, магазином, адресом и поддержкой"
            ],
            tags: [
                "Python",
                "Aiogram 3",
                "SQLite",
                "Telegram API",
                "FSM"
            ]
        },

        website: {
            index: "LIVE PROJECT / 02",
            title: "Сайт-портфолио MAD_ALEX",
            description:
                "Рабочий адаптивный сайт для презентации услуг разработчика. Он содержит анимации, портфолио, форму заявки, базу данных и серверную часть на Flask.",
            features: [
                "Адаптивный дизайн",
                "Неоновая стилистика",
                "Анимации появления",
                "Слайдер проектов",
                "Модальные окна",
                "Форма отправки заявки",
                "Сохранение заявок в SQLite",
                "Flask backend",
                "Подготовка к размещению на Render"
            ],
            tags: [
                "Flask",
                "HTML5",
                "CSS3",
                "JavaScript",
                "SQLite"
            ]
        },

        automation: {
            index: "DEMO / 03",
            title: "Система автоматизации процессов",
            description:
                "Демонстрационная система для объединения нескольких сервисов в единый рабочий процесс. Она показывает, как получать данные по API, сохранять их в базе и передавать результат боту или веб-интерфейсу.",
            features: [
                "Интеграция внешних API",
                "Автоматическая обработка данных",
                "Работа по расписанию",
                "Сохранение результатов",
                "Telegram-уведомления",
                "Логирование операций",
                "Обработка ошибок",
                "Веб-интерфейс управления"
            ],
            tags: [
                "Python",
                "REST API",
                "SQLite",
                "Automation",
                "Flask"
            ]
        }
    };

    const openModal = (projectKey) => {
        const project = projects[projectKey];

        if (!project) {
            return;
        }

        if (modalIndex) {
            modalIndex.textContent = project.index;
        }

        if (modalTitle) {
            modalTitle.textContent = project.title;
        }

        if (modalDescription) {
            modalDescription.textContent =
                project.description;
        }

        if (modalFeatures) {
            modalFeatures.innerHTML = "";

            project.features.forEach((feature) => {
                const listItem =
                    document.createElement("li");

                listItem.textContent = feature;
                modalFeatures.appendChild(listItem);
            });
        }

        if (modalTags) {
            modalTags.innerHTML = "";

            project.tags.forEach((tag) => {
                const tagElement =
                    document.createElement("span");

                tagElement.textContent = tag;
                modalTags.appendChild(tagElement);
            });
        }

        modal.classList.add("is-open");
        document.body.classList.add("modal-open");
    };

    const closeModal = () => {
        modal.classList.remove("is-open");
        document.body.classList.remove("modal-open");
    };

    openButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const projectKey =
                button.dataset.project;

            openModal(projectKey);
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            modal.classList.contains("is-open")
        ) {
            closeModal();
        }
    });
}


/* =========================================================
   SUCCESS MODAL
========================================================= */

function initSuccessModal() {
    const modal =
        document.getElementById("successModal");

    const closeButton =
        document.getElementById("successModalClose");

    const confirmButton =
        document.getElementById("successModalButton");

    if (!modal) {
        return;
    }

    const closeModal = () => {
        modal.classList.remove("is-open");
        document.body.classList.remove("modal-open");
    };

    if (closeButton) {
        closeButton.addEventListener(
            "click",
            closeModal
        );
    }

    if (confirmButton) {
        confirmButton.addEventListener(
            "click",
            closeModal
        );
    }

    const overlay =
        modal.querySelector(".success-modal__overlay");

    if (overlay) {
        overlay.addEventListener("click", closeModal);
    }

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            modal.classList.contains("is-open")
        ) {
            closeModal();
        }
    });
}

function openSuccessModal(message) {
    const modal =
        document.getElementById("successModal");

    const text =
        document.getElementById("successModalText");

    if (!modal) {
        return;
    }

    if (text && message) {
        text.textContent = message;
    }

    modal.classList.add("is-open");
    document.body.classList.add("modal-open");
}


/* =========================================================
   CONTACT FORM
========================================================= */

function initContactForm() {
    const form =
        document.getElementById("contactForm");

    const submitButton =
        document.getElementById("submitButton");

    const formMessage =
        document.getElementById("formMessage");

    if (!form || !submitButton) {
        return;
    }

    const submitText =
        submitButton.querySelector(
            ".submit-button__text"
        );

    const fields = {
        name: document.getElementById("name"),
        contact: document.getElementById("contact"),
        service: document.getElementById("service"),
        budget: document.getElementById("budget"),
        message: document.getElementById("message")
    };

    const clearErrors = () => {
        Object.values(fields).forEach((field) => {
            if (!field) {
                return;
            }

            const wrapper =
                field.closest(".form-field");

            if (wrapper) {
                wrapper.classList.remove("is-error");
            }
        });

        if (formMessage) {
            formMessage.className = "form-message";
            formMessage.textContent = "";
        }
    };

    const showFieldError = (field) => {
        if (!field) {
            return;
        }

        const wrapper =
            field.closest(".form-field");

        if (wrapper) {
            wrapper.classList.add("is-error");
        }
    };

    const showFormMessage = (message, type) => {
        if (!formMessage) {
            return;
        }

        formMessage.className =
            `form-message is-${type}`;

        formMessage.textContent = message;
    };

    const validateForm = () => {
        clearErrors();

        let isValid = true;

        const nameValue =
            fields.name?.value.trim() || "";

        const contactValue =
            fields.contact?.value.trim() || "";

        const messageValue =
            fields.message?.value.trim() || "";

        if (nameValue.length < 2) {
            showFieldError(fields.name);
            isValid = false;
        }

        if (contactValue.length < 3) {
            showFieldError(fields.contact);
            isValid = false;
        }

        if (messageValue.length < 10) {
            showFieldError(fields.message);
            isValid = false;
        }

        if (!isValid) {
            showFormMessage(
                "Проверьте заполнение обязательных полей.",
                "error"
            );
        }

        return isValid;
    };

    const setLoadingState = (isLoading) => {
        submitButton.disabled = isLoading;

        if (submitText) {
            submitText.textContent = isLoading
                ? "Отправляем..."
                : "Отправить идею";
        }

        submitButton.style.opacity =
            isLoading ? "0.7" : "1";

        submitButton.style.pointerEvents =
            isLoading ? "none" : "auto";
    };

    Object.values(fields).forEach((field) => {
        if (!field) {
            return;
        }

        field.addEventListener("input", () => {
            const wrapper =
                field.closest(".form-field");

            if (wrapper) {
                wrapper.classList.remove("is-error");
            }
        });

        field.addEventListener("change", () => {
            const wrapper =
                field.closest(".form-field");

            if (wrapper) {
                wrapper.classList.remove("is-error");
            }
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoadingState(true);
        clearErrors();

        const formData = new FormData(form);

        const requestData = {
            name:
                formData.get("name")?.toString().trim() ||
                "",

            contact:
                formData.get("contact")?.toString().trim() ||
                "",

            service:
                formData.get("service")?.toString().trim() ||
                "",

            budget:
                formData.get("budget")?.toString().trim() ||
                "",

            message:
                formData.get("message")?.toString().trim() ||
                ""
        };

        try {
            const response = await fetch("/send-request", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(requestData)
            });

            let result = {};

            try {
                result = await response.json();
            } catch (jsonError) {
                result = {};
            }

            if (!response.ok) {
                throw new Error(
                    result.message ||
                    result.error ||
                    "Не удалось отправить заявку."
                );
            }

            const successMessage =
                result.message ||
                "Спасибо! Я свяжусь с вами в ближайшее время.";

            showFormMessage(
                successMessage,
                "success"
            );

            openSuccessModal(successMessage);

            form.reset();
        } catch (error) {
            console.error(
                "Ошибка отправки формы:",
                error
            );

            showFormMessage(
                error.message ||
                "Произошла ошибка. Попробуйте ещё раз.",
                "error"
            );
        } finally {
            setLoadingState(false);
        }
    });
}


/* =========================================================
   PREMIUM HERO EFFECTS
========================================================= */
function initPremiumHeroEffects() {
    const root = document.documentElement;
    const hero = document.getElementById("home");
    const robot = document.querySelector(".hero-robot");

    if (!hero || !robot || window.matchMedia("(pointer: coarse)").matches) {
        return;
    }

    let frame = null;

    const update = (event) => {
        if (frame) {
            cancelAnimationFrame(frame);
        }

        frame = requestAnimationFrame(() => {
            const xPercent = (event.clientX / window.innerWidth) * 100;
            const yPercent = (event.clientY / window.innerHeight) * 100;
            root.style.setProperty("--mouse-x", `${xPercent}%`);
            root.style.setProperty("--mouse-y", `${yPercent}%`);

            const rect = hero.getBoundingClientRect();
            if (event.clientY < rect.top || event.clientY > rect.bottom) {
                return;
            }

            const localX = (event.clientX - rect.left) / rect.width - 0.5;
            const localY = (event.clientY - rect.top) / rect.height - 0.5;
            robot.style.setProperty("--robot-x", `${localX * 14}px`);
            robot.style.setProperty("--robot-y", `${localY * 10}px`);
        });
    };

    document.addEventListener("mousemove", update, { passive: true });
    hero.addEventListener("mouseleave", () => {
        robot.style.setProperty("--robot-x", "0px");
        robot.style.setProperty("--robot-y", "0px");
    });
}
