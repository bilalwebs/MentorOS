"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAddProject } from "@/hooks/useProjects";

export function ProjectForm() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [techInput, setTechInput] = useState("");
  const [techStack, setTechStack] = useState<string[]>([]);
  const addProject = useAddProject();

  const addTech = () => {
    const trimmed = techInput.trim();
    if (trimmed && !techStack.includes(trimmed)) {
      setTechStack([...techStack, trimmed]);
    }
    setTechInput("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    addProject.mutate(
      { title: title.trim(), description: description.trim() || undefined, tech_stack: techStack },
      {
        onSuccess: () => {
          setTitle("");
          setDescription("");
          setTechStack([]);
        },
      }
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Add a project</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="space-y-1.5">
            <Label htmlFor="project-title">Title</Label>
            <Input id="project-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. MentorOS" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="project-description">Description</Label>
            <Textarea
              id="project-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What does it do, what did you learn?"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="project-tech">Tech stack</Label>
            <div className="flex gap-2">
              <Input
                id="project-tech"
                value={techInput}
                onChange={(e) => setTechInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addTech();
                  }
                }}
                placeholder="Type a technology and press Enter"
              />
              <Button type="button" variant="secondary" onClick={addTech}>
                Add
              </Button>
            </div>
            {techStack.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {techStack.map((tech) => (
                  <Badge key={tech} variant="secondary" className="gap-1">
                    {tech}
                    <button
                      type="button"
                      onClick={() => setTechStack(techStack.filter((t) => t !== tech))}
                      aria-label={`Remove ${tech}`}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>
          <Button type="submit" disabled={addProject.isPending || !title.trim()}>
            <Plus className="h-4 w-4" /> Add Project
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
