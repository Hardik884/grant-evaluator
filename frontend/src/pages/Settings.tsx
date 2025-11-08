import { useState, useEffect } from 'react';
import { Save, ShieldCheck, SlidersHorizontal, Info } from 'lucide-react';
import { Card } from '../components/Card';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { evaluationService } from '../services/evaluationService';
import type { Settings as SettingsType } from '../types/evaluation';

export function Settings() {
  const [settings, setSettings] = useState<Partial<SettingsType>>({
    max_budget: 500000,
    chunk_size: 1000,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const data = await evaluationService.getSettings();
      if (data) {
        setSettings({
          max_budget: data.max_budget,
          chunk_size: data.chunk_size,
        });
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);

    try {
      await evaluationService.updateSettings(settings);
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save settings. Please try again.' });
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-6rem)] items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-2 border-secondary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-10 px-4 pb-24 pt-10 lg:px-8">
      <div className="space-y-3">
        <h1 className="text-3xl font-semibold text-white">Settings</h1>
        <p className="max-w-2xl text-sm text-slate-300">
          Adjust evaluation defaults and budget limits for future runs.
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1.15fr,0.85fr]">
        <Card className="space-y-8">
          <div className="flex items-center gap-3 text-secondary">
            <SlidersHorizontal className="h-5 w-5" />
            <div>
              <span className="text-xs uppercase tracking-[0.25em] text-secondary">Evaluation</span>
              <h2 className="mt-1 text-xl font-semibold text-white">Defaults</h2>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <Input
              type="number"
              label="Maximum Allowable Budget ($)"
              value={settings.max_budget ?? ''}
              onChange={(e) => setSettings({ ...settings, max_budget: Number(e.target.value) })}
              placeholder="500000"
            />

            <Input
              type="number"
              label="Document Chunk Size"
              value={settings.chunk_size ?? ''}
              onChange={(e) => setSettings({ ...settings, chunk_size: Number(e.target.value) })}
              placeholder="1000"
            />
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-5 text-sm text-slate-300">
            <h3 className="mb-2 text-base font-semibold text-white">Quick help</h3>
            <ul className="space-y-2">
              <li>
                <strong className="text-slate-100">Max budget</strong>: Anything above this value is flagged in results.
              </li>
              <li>
                <strong className="text-slate-100">Chunk size</strong>: Number of tokens processed per document slice.
              </li>
            </ul>
          </div>

          {message && (
            <div
              className={`rounded-2xl border px-4 py-3 text-sm ${
                message.type === 'success'
                  ? 'border-secondary/60 bg-secondary/10 text-secondary'
                  : 'border-error/60 bg-error/10 text-error'
              }`}
            >
              {message.text}
            </div>
          )}

          <div className="flex justify-end">
            <Button onClick={handleSave} isLoading={isSaving} className="flex items-center gap-2">
              <Save className="h-5 w-5" />
              Save changes
            </Button>
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="space-y-3">
            <div className="flex items-center gap-2 text-secondary">
              <Info className="h-5 w-5" />
              <h3 className="text-lg font-semibold text-white">System info</h3>
            </div>
            <ul className="space-y-2 text-sm text-slate-300">
              <li><strong className="text-slate-100">Version</strong>: 1.0.0</li>
              <li><strong className="text-slate-100">Model stack</strong>: gemini-2.0-flash + retrieval agents</li>
            </ul>
          </Card>

          <Card className="space-y-3">
            <div className="flex items-center gap-2 text-secondary">
              <ShieldCheck className="h-5 w-5" />
              <h3 className="text-lg font-semibold text-white">Data & safety</h3>
            </div>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>Uploads are encrypted and cleared after 24 hours.</li>
              <li>Reviewer changes remain in an audit log.</li>
              <li>Prompts avoid storing applicant data.</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}
