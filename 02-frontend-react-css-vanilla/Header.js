import React from 'react';
import LanguageSelector from './languageSelector';

const Header = ({ onLanguageChange }) => {
    return (
        <header>
            <h1>My Application</h1>
            <LanguageSelector onLanguageChange={onLanguageChange} />
        </header>
    );
};

export default Header;