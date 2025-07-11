import React from "react"

export default function ImageGallery({ images }) {
	if (!images?.length) return null;

	return (
		<div>
			<h3>Best Images</h3>
			<div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
				{
					images.map(({ uuidName, originalName, url, tags, score }) => (
						<div key={uuidName} style={{ textAlign: "center" }}>
							<img src={url} alt={originalName} style={{ width: "200px", height: "200px", objectFit: "cover" }} />
							<div style={{ fontSize: "0.75rem", marginTop: "4px" }}><strong>Score:</strong> {score.toFixed(2)} {originalName}</div>
						</div>
					))
				}
			</div>
		</div>
	);
}