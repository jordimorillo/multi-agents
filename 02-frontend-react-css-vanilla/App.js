import React, { useState, useEffect } from 'react';
import LanguageSelector from './languageSelector';
import detectLanguage from './languageDetection';

const App = () => {
    const [language, setLanguage] = useState('en');

    useEffect(() => {
        const initialLanguage = detectLanguage();
        setLanguage(initialLanguage);
    }, []);

    const handleLanguageChange = (newLanguage) => {
        setLanguage(newLanguage);
    };

    const content = {
        en: {
            welcome: "Welcome to our website!",
            description: "This is a sample application to demonstrate language switching."
        },
        es: {
            welcome: "¡Bienvenido a nuestro sitio web!",
            description: "Esta es una aplicación de muestra para demostrar el cambio de idioma."
        }
    };

    return (
        <div>
            <header>
                <LanguageSelector onLanguageChange={handleLanguageChange} />
            </header>
            <main>
                <h1>{content[language].welcome}</h1>
                <p>{content[language].description}</p>
            </main>
        </div>
    );
};

export default App;