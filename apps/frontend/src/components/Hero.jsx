import React, { useState, useEffect} from 'react';
import styles from './Hero.module.css';

const phrases = [
    "with precision",
    "for impact",
    "with care",
    "to captivate",
    "by Theia Sense"
]
export default function Hero() {
    const fixedText = "Every image, chosen"
    const [index, setIndex] = useState(0);
    const [fade, setFade] = useState(true);

    useEffect(() => {
        if (index === phrases.length - 1) return; // stop at last phrase

        // Run this function after 2000ms
        const timer = setTimeout(() => {
            setFade(false); // Start fade out
            setTimeout(() => {
                setIndex((prev) => prev + 1);
                setFade(true); // Fade in next phrase
            },600); // fade out duration
        }, 2000); // phrase duration

        return () => clearTimeout(timer);
    }, [index]);

    const handleClick = () => {
        const layoutElement = document.getElementById('appLayout');
        if (layoutElement) {
            layoutElement.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <section className={styles.hero}>
            <div className={styles.content}>
                <div className={styles.left}>{fixedText}</div>
                <div className={`${styles.right} ${fade ? styles.fadeIn : styles.fadeOut}`}>
                    {phrases[index]}
                </div>
            </div>

            <button onClick={handleClick} className={`btn btn-secondary ${styles.ctaButton}`}>
                Find Your Best Shots
            </button>
        </section>

    );
};

//<section className={styles.hero}>
//    <div className={styles.contentWrapper}>
//        <div className={styles.taglines}>
//            <span className={styles.tagline}>From hundreds to favorites, instantly.</span>
//            <span className={styles.tagline}>See only your best shots, every time.</span>
//            <span className={styles.tagline}>Automatic picks, zero guesswork.</span>
//            <span className={styles.tagline}>Quickly find photos that truly stand out.</span>
//        </div>

//        <div className={styles.content}>
//            <div className={styles.left}>{fixedText}</div>
//            <div className={`${styles.right} ${fade ? styles.fadeIn : styles.fadeOut}`}>
//                {phrases[index]}
//            </div>
//        </div>
//    </div>

//    <button onClick={handleClick} className={styles.ctaButton}>
//        Find Your Best Shots
//    </button>
//</section>