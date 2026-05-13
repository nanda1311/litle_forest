document.addEventListener("DOMContentLoaded", function () {

    const mainTitle = document.querySelector(".main-card h3");
    const mainImage = document.querySelector(".main-card img");
    const cardsContainer = document.querySelector(".plant-cards");

    let interval;

    function rotatePlants() {

        const cards = cardsContainer.querySelectorAll("a");
        if (cards.length === 0) return;

        const currentCard = cards[0];

        const imgEl = currentCard.querySelector("img");
        const textEl = currentCard.querySelector("p");

        if (!imgEl || !textEl) return;

        const cardImg = imgEl.src;
        const cardText = textEl.innerHTML;

        const mainImgSrc = mainImage.src;
        const mainText = mainTitle.innerHTML;

        // Fade out
        mainImage.style.opacity = "0";
        mainTitle.style.opacity = "0";

        setTimeout(() => {

            // Swap content
            mainImage.src = cardImg;
            mainTitle.innerHTML = cardText;

            imgEl.src = mainImgSrc;
            textEl.innerHTML = mainText;

            cardsContainer.appendChild(currentCard);

            // Fade in
            mainImage.style.opacity = "1";
            mainTitle.style.opacity = "1";

        }, 300);
    }

    function startRotation() {
        interval = setInterval(rotatePlants, 3000);
    }

    function stopRotation() {
        clearInterval(interval);
    }

    startRotation();

    const section = document.querySelector(".plants-section");

    if (section) {
        section.addEventListener("mouseenter", stopRotation);
        section.addEventListener("mouseleave", startRotation);
    }
});