import React from "react";
import JSZip from "jszip";
import { FaDownload } from "react-icons/fa";
import styles from "./ImageGallery.module.css";

export default function ImageGallery({ images }) {
	if (!images?.length) return null;

	const handleDownloadZip = async () => {
		const zip = new JSZip();
		const folder = zip.folder("best-images");

		await Promise.all(
			images.map(async ({ uuidName, originalName, url }) => {
				try {
					const response = await fetch(url);
					const blob = await response.blob();
					const filename = originalName || `${uuidName}.jpg`;
					folder.file(filename, blob);
				} catch (err) {
					console.error(`Failed to download image: ${url}`, err);
				}
			})
		);

		const zipBlob = await zip.generateAsync({ type: "blob" });
		const zipUrl = URL.createObjectURL(zipBlob);

		const a = document.createElement("a");
		a.href = zipUrl;
		a.download = "best-images.zip";
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);

		URL.revokeObjectURL(zipUrl);
	};

	return (
		<div className={styles.wrapper }>
			<div className={styles.header}>
			<h2>Best Images</h2>
			<button className={styles.downloadButton} onClick={handleDownloadZip}>
				<FaDownload />
				</button>
			</div>
			<div className={styles.container}>
				{images.map(({ uuidName, originalName, thumbnailUrl, score }) => (
					<div key={uuidName} className={styles.imageWrapper}>
						<img src={thumbnailUrl} alt={originalName} className={styles.image} />
						<div className={styles.score}>
							<strong>Score:</strong> {score.toFixed(2)}
						</div>
					</div>
				))}
			</div>
		</div>
	);
}
