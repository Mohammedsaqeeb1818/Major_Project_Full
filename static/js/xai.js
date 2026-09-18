
async function generateAIExplanation() {

    const output = document.getElementById("ai-output");
    const config = document.getElementById("ai-config");

    // Show loading message
    output.textContent = "Generating AI explanation...\nPlease wait...";

    try {

        // Read configuration from HTML
        const streamUrl = config.dataset.streamUrl;

        const pageData = {
            prediction: JSON.parse(config.dataset.prediction),
            input_data: JSON.parse(config.dataset.input),
            explanation: JSON.parse(config.dataset.explanation),
            recommendations: JSON.parse(config.dataset.recommendations)
        };

        // Send request to Flask
        const response = await fetch(streamUrl, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(pageData)

        });

        // Check response
        if (!response.ok) {

            output.textContent =
                "Failed to generate AI explanation.";

            return;
        }

        // Check streaming support
        if (!response.body) {

            output.textContent =
                "Streaming is not supported by this response.";

            return;
        }

        // Read streaming response
        const reader = response.body.getReader();

        const decoder = new TextDecoder();

        output.textContent = "";

        while (true) {

            const { value, done } =
                await reader.read();

            if (done) {
                break;
            }

            // Convert received bytes into text
            const chunk =
                decoder.decode(value, { stream: true });

            // Display response progressively
            output.textContent += chunk;

        }

        // Decode any remaining text
        output.textContent += decoder.decode();

    } catch (error) {

        console.error("AI Error:", error);

        output.textContent =
            "Error connecting to AI service. Please try again.";

    }

}