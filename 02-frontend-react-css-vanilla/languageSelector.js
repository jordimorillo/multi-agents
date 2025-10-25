// Language selector component
import React, { useState } from 'react';

const LanguageSelector = ({ onLanguageChange }) => {
    const [selectedLanguage, setSelectedLanguage] = useState('en');

    const handleChange = (event) => {
        const newLanguage = event.target.value;
        setSelectedLanguage(newLanguage);
        onLanguageChange(newLanguage);
    };

    return (
        <select value={selectedLanguage} onChange={handleChange}>
            <option value="en">English</option>
            <option value="es">Español</option>
        </select>
    );
};

export default LanguageSelector;