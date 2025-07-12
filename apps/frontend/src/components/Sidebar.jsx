import React, { useState, useEffect} from "react"
import styles from "./Sidebar.module.css"
import { FiX, FiImage } from "react-icons/fi";
export default function Sidebar({ images, onFilesRemoved, isUploading }) {
	
	const [previewUrls, setPreviewUrls] = useState([]);

	useEffect(() => {
		const urls = images.map(({ file }) => ({
			name: file.name,
			url: URL.createObjectURL(file),
		}));

		setPreviewUrls(urls);

		// Clean on unmount
		return () => {
			urls.forEach(({ url }) => URL.revokeObjectURL(url));
		};
	}, [images]);

	if (!images?.length) return null;

	return (
		<aside className={styles.wrapper}>
			<div className={styles.header}>
				<h2>All Images</h2>
				<button
					onClick={() => onFilesRemoved()}
					disabled={images.length === 0 || isUploading}
					className={styles.removeAllBtn}
				>
					Remove all
				</button>

			</div>
			<ul className={styles.container}>
				{images.map(({ file, originalName }) => {
					const preview = previewUrls.find((u) => u.name === file.name);
					return (
						preview && (
							<li key={file.name} className={styles.items}>
								<FiImage className={styles.imageIcon} />
								<span className={styles.filename}>{originalName}</span>
								<button
									className={styles.removeBtn}
									onClick={() => onFilesRemoved(file.name)}
									aria-label="Remove file"
									disabled={isUploading}
									type="button"
								>
									<FiX />
								</button>
							</li>
						)
					);
				})}
			</ul>
		</aside>
	);
}