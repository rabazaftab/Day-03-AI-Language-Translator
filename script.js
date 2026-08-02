const inputText = document.getElementById("inputText");
const charCount = document.getElementById("charCount");
const output = document.getElementById("translationOutput");
const statusText = document.getElementById("status");
const translateButton = document.getElementById("translateButton");


inputText.addEventListener("input", () => {

    const length = inputText.value.length;

    charCount.textContent = `${length} / 5000`;

});


async function translateText() {

    const text = inputText.value.trim();

    const sourceLanguage =
        document.getElementById("sourceLanguage").value;

    const targetLanguage =
        document.getElementById("targetLanguage").value;


    if (!text) {

        output.textContent =
            "Please enter some text to translate.";

        return;

    }


    if (sourceLanguage === targetLanguage) {

        output.textContent =
            "Please select different languages.";

        return;

    }


    translateButton.disabled = true;

    translateButton.textContent = "Translating...";

    statusText.textContent = "AI is working...";

    output.textContent = "";


    try {

        const response = await fetch("/translate", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                text: text,

                source_language: sourceLanguage,

                target_language: targetLanguage

            })

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.error || "Translation failed."
            );

        }


        output.textContent = data.translation;

        statusText.textContent =
            `${data.source_language} → ${data.target_language}`;

    }

    catch (error) {

        output.textContent =
            "Something went wrong. Please try again.";

        statusText.textContent = "Error";

        console.error(error);

    }

    finally {

        translateButton.disabled = false;

        translateButton.textContent = "Translate";

    }

}


function copyTranslation() {

    const text = output.textContent.trim();


    if (!text ||
        text === "Your translation will appear here.") {

        return;

    }


    navigator.clipboard.writeText(text);

}


function clearText() {

    inputText.value = "";

    output.textContent =
        "Your translation will appear here.";

    charCount.textContent = "0 / 5000";

    statusText.textContent = "";

}


function swapLanguages() {

    const source =
        document.getElementById("sourceLanguage");

    const target =
        document.getElementById("targetLanguage");


    const oldSource = source.value;

    source.value = target.value;

    target.value = oldSource;

}