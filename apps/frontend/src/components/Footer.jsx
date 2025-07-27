import React from 'react';
import styles from './Footer.module.css';

export default function Footer() {
    return (
        <section className={styles.footer}>
            <div className={styles.content}>
                
                
                    <p>Developed by:</p>
                    <ul>
                        <li>
                        Aditya Patel
                        <div className={styles.contact }>
                            <a href="mailto:imadityapatel149@gmail.com">Contact</a>
                            <span style={{ fontWeight: 300 }}> | </span>
                            <a href="https://github.com/adityapatel149" target="_blank" rel="noopener noreferrer">GitHub</a>
                        </div>
                        </li>
                        <li>
                        Rutansh Suthar
                        <div className={styles.contact}>
                            <a href="mailto:rutanshsuthar4u@gmail.com">Contact</a> 
                            <span style={{ fontWeight: 300 }}> | </span>
                            <a href="https://github.com/rutanshsuthar" target="_blank" rel="noopener noreferrer"> GitHub</a>
                        </div>
                        </li>
                </ul>
                <h1>THEIA SENSE</h1>

            </div>
        </section>
    );
}


