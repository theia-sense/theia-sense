import React, { useState, useMemo } from 'react';
import styles from './TagFilter.module.css';
import {
    FiChevronUp,
    FiX,
    FiTrash2,
    FiTag,
    FiFilter,
    FiSearch
} from 'react-icons/fi';

export default function TagFilter({ images, onTagFilter, selectedTags = [] }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [isCollapsed, setIsCollapsed] = useState(true); 

    const toggleCollapse = () => setIsCollapsed(prev => !prev); 

    const uniqueTags = useMemo(() => {
        if (!images?.length) return [];
        const allTags = images.flatMap(image => image.tags || []);
        const tagCounts = allTags.reduce((acc, tag) => {
            acc[tag] = (acc[tag] || 0) + 1;
            return acc;
        }, {});
        return Object.entries(tagCounts)
            .sort(([a, aCount], [b, bCount]) => {
                if (bCount !== aCount) return bCount - aCount;
                return a.localeCompare(b);
            })
            .map(([tag, count]) => ({ tag, count }));
    }, [images]);

    const filteredTags = useMemo(() => {
        const tags = searchTerm
            ? uniqueTags.filter(({ tag }) =>
                tag.toLowerCase().includes(searchTerm.toLowerCase())
            )
            : uniqueTags;
        return tags.sort((a, b) => {
            const aSelected = selectedTags.includes(a.tag);
            const bSelected = selectedTags.includes(b.tag);
            if (aSelected && !bSelected) return -1;
            if (!aSelected && bSelected) return 1;
            return 0;
        });
    }, [uniqueTags, searchTerm, selectedTags]);

    const handleTagToggle = (tag) => {
        const isSelected = selectedTags.includes(tag);
        const newSelectedTags = isSelected
            ? selectedTags.filter(t => t !== tag)
            : [...selectedTags, tag];
        onTagFilter(newSelectedTags);
    };

    const clearAllTags = () => {
        onTagFilter([]);
    };

    if (!uniqueTags.length) return null;

    return (
        <div className={styles.filterContainer}>
            {/* Entire header is clickable */}
            <button
                className={styles.sectionHeader}
                onClick={toggleCollapse}
                aria-expanded={!isCollapsed}
                type="button"
            >
                <div className={styles.titleSection}>
                    <div className={styles.starWrapper}>
                        <svg
                            className={styles.starIcon}
                            viewBox="0 0 24 24"
                            fill="url(#filterGradient)"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <defs>
                                <linearGradient id="filterGradient" x1="0" y1="0" x2="1" y2="1">
                                    <stop offset="0%" stopColor="#667eea" />
                                    <stop offset="100%" stopColor="#764ba2" />
                                </linearGradient>
                            </defs>
                            <g transform="scale(0.9) translate(1.3 1.3)">
                                <path
                                    d="M3 4a1 1 0 0 1 1-1h16a1 1 0 0 1 .78 1.625L15 12.5V19a1 1 0 0 1-1.447.894l-4-2A1 1 0 0 1 9 17v-4.5L3.22 5.625A1 1 0 0 1 3 4Z"
                                    stroke="none"
                                />
                            </g>
                        </svg>


                    </div>
                    <h3 className={styles.filterTitle}>Filter by Tags</h3>
                    {selectedTags.length > 0 && (
                        <span className={styles.activeCount}>
                            {selectedTags.length} active
                        </span>
                    )}
                </div>

                <FiChevronUp
                    className={`${styles.chevronIcon} ${isCollapsed ? styles.collapsed : ''}`}
                />
            </button>

            {/* Clear All should not toggle collapse 
            {selectedTags.length > 0 && (
                <button className={styles.clearAllButton} onClick={clearAllTags}>
                    <FiTrash2 className={styles.clearIcon} />
                    Clear All
                </button>
            )*/}

            {/* Collapsible content */}
            {!isCollapsed && (
                <>
                    <div className={styles.searchSection}>
                        <div className={styles.searchInputContainer}>
                            <FiSearch className={styles.searchIcon} />
                            <input
                                type="text"
                                placeholder="Search tags..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className={styles.searchInput}
                            />
                        </div>
                    </div>

                    <div className={styles.pillTagsGrid}>
                        {filteredTags.map(({ tag, count }) => {
                            const isSelected = selectedTags.includes(tag);
                            return (
                                <button
                                    key={tag}
                                    className={`${styles.pillTag} ${isSelected ? styles.pillSelected : ''}`}
                                    onClick={() => handleTagToggle(tag)}
                                    aria-pressed={isSelected}
                                >
                                    <FiTag className={styles.pillTagIcon} />
                                    <span>{tag}</span>
                                    <span className={styles.pillTagCount}>({count})</span>
                                    {isSelected && <FiX className={styles.pillRemoveIcon} />}
                                </button>
                            );
                        })}
                        {filteredTags.length === 0 && searchTerm && (
                            <div className={styles.noResults}>
                                <FiSearch className={styles.noResultsIcon} />
                                <span>No tags found for "{searchTerm}"</span>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>

    );
}
