import { useState } from 'react';
import { Copy, Check, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { truncateHash } from '@/lib/utils';
import { useToast } from '@/hooks/useToast';

export function BlockchainHash({ hash, explorerUrl, className }) {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const handleCopy = async () => {
    if (!hash) return;
    await navigator.clipboard.writeText(hash);
    setCopied(true);
    toast({ title: 'Copied', description: 'Transaction hash copied to clipboard' });
    setTimeout(() => setCopied(false), 2000);
  };

  if (!hash) return <span className="text-muted-foreground">—</span>;

  return (
    <div className={`flex items-center gap-1 font-mono text-sm ${className || ''}`}>
      <span title={hash}>{truncateHash(hash, 10, 8)}</span>
      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleCopy}>
        {copied ? <Check className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3" />}
      </Button>
      {explorerUrl && (
        <a href={`${explorerUrl}${hash}`} target="_blank" rel="noopener noreferrer">
          <Button variant="ghost" size="icon" className="h-7 w-7">
            <ExternalLink className="h-3 w-3" />
          </Button>
        </a>
      )}
    </div>
  );
}
