import React from "react"

export default function ImageGallery({ images }) {
	if (!images?.length) return null;

	return (
		<div>
			<h3>Best Images</h3>
			<div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
				{
					images.map(({ name, url, tags, score }) => (
						<div key={name} style={{ textAlign: "center" }}>
							<img src={url} alt={name} style={{ width: "200px", height: "200px", objectFit: "cover" }} />
							<div style={{ fontSize: "0.75rem", marginTop: "4px" }}><strong>Score:</strong> {score.toFixed(2)}</div>
						</div>
					))
				}
			</div>
		</div>
	);
}