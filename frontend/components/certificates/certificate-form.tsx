"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAddCertificate } from "@/hooks/useCertificates";

export function CertificateForm() {
  const [title, setTitle] = useState("");
  const [issuer, setIssuer] = useState("");
  const [dateEarned, setDateEarned] = useState("");
  const addCertificate = useAddCertificate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    addCertificate.mutate(
      { title: title.trim(), issuer: issuer.trim() || undefined, date_earned: dateEarned || undefined },
      {
        onSuccess: () => {
          setTitle("");
          setIssuer("");
          setDateEarned("");
        },
      }
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Add a certificate</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="grid gap-3 sm:grid-cols-3">
          <div className="space-y-1.5 sm:col-span-1">
            <Label htmlFor="cert-title">Title</Label>
            <Input id="cert-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="AWS Cloud Practitioner" />
          </div>
          <div className="space-y-1.5 sm:col-span-1">
            <Label htmlFor="cert-issuer">Issuer</Label>
            <Input id="cert-issuer" value={issuer} onChange={(e) => setIssuer(e.target.value)} placeholder="AWS" />
          </div>
          <div className="space-y-1.5 sm:col-span-1">
            <Label htmlFor="cert-date">Date earned</Label>
            <Input id="cert-date" type="date" value={dateEarned} onChange={(e) => setDateEarned(e.target.value)} />
          </div>
          <Button type="submit" className="sm:col-span-3 sm:w-fit" disabled={addCertificate.isPending || !title.trim()}>
            <Plus className="h-4 w-4" /> Add Certificate
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
