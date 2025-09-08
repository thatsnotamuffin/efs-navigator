export async function fetchMetadata(path) {
  const response = await fetch(`/metadata/${path}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch metadata for ${path}`);
  }
  return response.json();
}

export function downloadFile(path) {
  const link = document.createElement("a");
  link.href = `/download/${path}`;
  link.download = "";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
