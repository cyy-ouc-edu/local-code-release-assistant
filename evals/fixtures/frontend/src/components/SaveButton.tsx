type SaveButtonProps = {
  onSave: () => void;
  isSaving?: boolean;
};

export function SaveButton({ onSave, isSaving = false }: SaveButtonProps) {
  return (
    <button disabled={isSaving} onClick={onSave}>
      {isSaving ? "Saving..." : "Save"}
    </button>
  );
}
