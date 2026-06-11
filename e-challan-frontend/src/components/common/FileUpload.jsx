import { useCallback, useState } from 'react';
import { Upload, X, FileImage, File } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
const MAX_SIZE_MB = 10;

export function FileUpload({ onFilesSelected, multiple = false, accept, maxSizeMb = MAX_SIZE_MB, className }) {
  const [files, setFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');

  const validateFile = (file) => {
    const types = accept ? accept.split(',').map((t) => t.trim()) : ACCEPTED_TYPES;
    if (!types.some((t) => file.type.match(t.replace('*', '.*')) || file.type === t)) {
      return 'Invalid file type';
    }
    if (file.size > maxSizeMb * 1024 * 1024) {
      return `File must be under ${maxSizeMb}MB`;
    }
    return null;
  };

  const handleFiles = useCallback(
    (fileList) => {
      const incoming = Array.from(fileList);
      const valid = [];
      for (const file of incoming) {
        const err = validateFile(file);
        if (err) {
          setError(err);
          return;
        }
        valid.push(file);
      }
      setError('');
      const updated = multiple ? [...files, ...valid] : valid.slice(0, 1);
      setFiles(updated);
      onFilesSelected?.(updated);
    },
    [files, multiple, onFilesSelected, accept, maxSizeMb]
  );

  const removeFile = (index) => {
    const updated = files.filter((_, i) => i !== index);
    setFiles(updated);
    onFilesSelected?.(updated);
  };

  return (
    <div className={cn('space-y-3', className)}>
      <div
        className={cn(
          'relative flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors',
          dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50',
          error && 'border-destructive'
        )}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragActive(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => document.getElementById('file-upload-input')?.click()}
      >
        <input
          id="file-upload-input"
          type="file"
          className="hidden"
          multiple={multiple}
          accept={accept || ACCEPTED_TYPES.join(',')}
          onChange={(e) => handleFiles(e.target.files)}
        />
        <Upload className="mb-2 h-8 w-8 text-muted-foreground" />
        <p className="text-sm font-medium">Drop files here or click to upload</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Images or PDF up to {maxSizeMb}MB
        </p>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((file, i) => (
            <li key={`${file.name}-${i}`} className="flex items-center justify-between rounded-md border p-2 text-sm">
              <div className="flex items-center gap-2">
                {file.type.startsWith('image/') ? (
                  <FileImage className="h-4 w-4 text-primary" />
                ) : (
                  <File className="h-4 w-4 text-primary" />
                )}
                <span className="truncate max-w-[200px]">{file.name}</span>
                <span className="text-muted-foreground">({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => removeFile(i)}>
                <X className="h-4 w-4" />
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
