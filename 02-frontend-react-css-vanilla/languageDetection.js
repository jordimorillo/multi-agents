// Language detection script
function detectLanguage() {
    const language = navigator.language || navigator.userLanguage;
    return language.split('-')[0]; // Return language code (e.g., 'en', 'es')
}

// Export the function for use in other modules
export default detectLanguage;