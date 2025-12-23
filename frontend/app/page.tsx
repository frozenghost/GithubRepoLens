import { AnalysisFeature } from "@/components/analysis-feature";
import { LanguageSwitcher } from "@/components/language-switcher";

export default function Home() {
  return (
    <main className="min-h-screen relative overflow-hidden bg-background">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full mix-blend-multiply filter blur-3xl animate-blob bg-(--color-blob-1)"
        />
        <div 
          className="absolute top-0 right-1/4 w-[500px] h-[500px] rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000 bg-(--color-blob-2)"
        />
        <div 
          className="absolute -bottom-8 left-1/3 w-[500px] h-[500px] rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000 bg-(--color-blob-3)"
        />
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center mask-[linear-gradient(180deg,white,rgba(255,255,255,0))]" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col min-h-screen">
        {/* Header */}
        <header className="flex justify-between items-center mb-16">
          <div className="flex items-center gap-2">
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xl bg-linear-to-br from-primary to-secondary text-primary-foreground"
            >
              L
            </div>
            <span className="font-bold text-xl tracking-tight text-card-foreground">
              RepoLens
            </span>
          </div>
          <LanguageSwitcher />
        </header>

        {/* Hero Section & Analysis Feature */}
        <AnalysisFeature />
        
        {/* Footer */}
        <footer className="mt-16 py-8 text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} GithubRepoLens. Built for the future.</p>
        </footer>
      </div>
    </main>
  );
}
