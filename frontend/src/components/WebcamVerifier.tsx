type Props = { onCapture: (base64: string) => void };

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] || "");
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export function WebcamVerifier({ onCapture }: Props) {
  return (
    <input
      type="file"
      accept="image/*"
      capture="user"
      onChange={async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        onCapture(await fileToBase64(file));
      }}
    />
  );
}
