import { Database, Zap, Palette, Package } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  const features = [
    {
      title: "Next.js 16 + App Router",
      description: "Framework React moderno com renderização do lado do servidor",
      icon: Zap,
      color: "text-blue-500"
    },
    {
      title: "Prisma + PostgreSQL",
      description: "ORM type-safe com suporte a PostgreSQL",
      icon: Database,
      color: "text-green-500"
    },
    {
      title: "Tailwind CSS + shadcn/ui",
      description: "Componentes de UI modernos e personalizáveis",
      icon: Palette,
      color: "text-purple-500"
    },
    {
      title: "TypeScript + Lucide Icons",
      description: "Type safety completo com ícones bonitos",
      icon: Package,
      color: "text-orange-500"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <main className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Print IA
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Projeto Next.js configurado com TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons e Prisma
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="border-2 hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <Icon className={`w-8 h-8 ${feature.color}`} />
                    <CardTitle>{feature.title}</CardTitle>
                  </div>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button size="lg" className="w-full sm:w-auto">
            Começar a Desenvolver
          </Button>
          <Button size="lg" variant="outline" className="w-full sm:w-auto">
            Ver Documentação
          </Button>
        </div>

        {/* Setup Info */}
        <Card className="mt-12 border-yellow-200 dark:border-yellow-900 bg-yellow-50 dark:bg-yellow-950/20">
          <CardHeader>
            <CardTitle className="text-yellow-800 dark:text-yellow-200">
              ⚠️ Próximos Passos
            </CardTitle>
            <CardDescription className="text-yellow-700 dark:text-yellow-300">
              Para começar a usar o Prisma:
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-yellow-700 dark:text-yellow-300">
            <ol className="list-decimal list-inside space-y-2">
              <li>Configure a <code className="bg-yellow-100 dark:bg-yellow-900 px-2 py-1 rounded">DATABASE_URL</code> no arquivo <code className="bg-yellow-100 dark:bg-yellow-900 px-2 py-1 rounded">.env</code></li>
              <li>Execute <code className="bg-yellow-100 dark:bg-yellow-900 px-2 py-1 rounded">npx prisma generate</code></li>
              <li>Execute <code className="bg-yellow-100 dark:bg-yellow-900 px-2 py-1 rounded">npx prisma db push</code></li>
              <li>Consulte o <code className="bg-yellow-100 dark:bg-yellow-900 px-2 py-1 rounded">README_SETUP.md</code> para mais detalhes</li>
            </ol>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

