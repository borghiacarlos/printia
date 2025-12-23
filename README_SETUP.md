# Print IA - Setup Guide

Este projeto foi inicializado com Next.js 16, TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons e Prisma com PostgreSQL.

## 🚀 Tecnologias

- **Next.js 16** com App Router
- **TypeScript**
- **Tailwind CSS** para estilização
- **shadcn/ui** - Componentes de UI
- **Lucide Icons** - Ícones React
- **Prisma** - ORM para PostgreSQL
- **ESLint** - Linting

## 📋 Pré-requisitos

- Node.js 18.18 ou superior
- PostgreSQL instalado e rodando

## 🔧 Configuração do Banco de Dados

1. **Configure a URL do banco de dados** no arquivo `.env`:

```env
DATABASE_URL="postgresql://usuario:senha@localhost:5432/nome_do_banco?schema=public"
```

Substitua:
- `usuario` pelo seu usuário do PostgreSQL
- `senha` pela sua senha
- `nome_do_banco` pelo nome do banco que você criou

2. **Gere o Prisma Client**:

```bash
npx prisma generate
```

3. **Crie as tabelas no banco de dados**:

```bash
npx prisma db push
```

Ou, se preferir usar migrations:

```bash
npx prisma migrate dev --name init
```

## 🎯 Uso do Prisma

O arquivo `lib/prisma.ts` contém a instância singleton do Prisma Client. Use-o em suas rotas API e Server Components:

```typescript
import { prisma } from '@/lib/prisma'

// Exemplo de uso
const users = await prisma.user.findMany()
```

## 🎨 Adicionando Componentes shadcn/ui

Para adicionar componentes do shadcn/ui:

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
# etc...
```

Os componentes serão adicionados em `components/ui/`.

## 📦 Usando Lucide Icons

```typescript
import { Home, User, Settings } from 'lucide-react'

export default function Example() {
  return (
    <div>
      <Home className="w-6 h-6" />
      <User className="w-6 h-6" />
      <Settings className="w-6 h-6" />
    </div>
  )
}
```

## 🏃 Executar o Projeto

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar build de produção
npm start
```

O projeto estará disponível em [http://localhost:3000](http://localhost:3000).

## 📁 Estrutura do Projeto

```
print_ia/
├── app/                    # App Router (páginas e rotas API)
│   ├── layout.tsx         # Layout raiz
│   ├── page.tsx           # Página inicial
│   └── globals.css        # Estilos globais
├── components/            # Componentes React
│   └── ui/               # Componentes shadcn/ui
├── lib/                  # Utilitários e configurações
│   ├── prisma.ts         # Cliente Prisma
│   ├── utils.ts          # Funções utilitárias
│   └── generated/        # Prisma Client gerado
│       └── prisma/
├── prisma/
│   └── schema.prisma     # Schema do banco de dados
├── public/               # Arquivos estáticos
└── .env                  # Variáveis de ambiente
```

## 🗄️ Prisma Studio

Para visualizar e editar seus dados visualmente:

```bash
npx prisma studio
```

Isso abrirá uma interface web em [http://localhost:5555](http://localhost:5555).

## 📝 Próximos Passos

1. Configure sua conexão com o PostgreSQL no arquivo `.env`
2. Customize o schema do Prisma em `prisma/schema.prisma`
3. Execute `npx prisma generate` e `npx prisma db push`
4. Comece a desenvolver suas páginas em `app/`
5. Adicione componentes shadcn/ui conforme necessário

## 🔍 Recursos Úteis

- [Documentação Next.js](https://nextjs.org/docs)
- [Documentação Prisma](https://www.prisma.io/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Lucide Icons](https://lucide.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
