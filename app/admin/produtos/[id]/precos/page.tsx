import { prisma } from "@/lib/prisma";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { PriceForm } from "./components/price-form";
import { PriceActions } from "./components/price-actions";

export default async function ProductPricesPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const { id } = await params;

    // Verify product exists
    const product = await prisma.product.findUnique({
        where: { id },
        include: {
            prices: {
                orderBy: { minQuantity: "asc" },
            },
        },
    });

    if (!product) {
        return <div>Produto não encontrado.</div>;
    }

    return (
        <div className="container mx-auto py-10">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-muted-foreground mb-2">
                    <Link href="/admin/produtos" className="hover:text-foreground flex items-center gap-1">
                        <ArrowLeft className="h-4 w-4" /> Voltar para Produtos
                    </Link>
                    <span>/</span>
                    <span>Preços</span>
                </div>
                <h1 className="text-3xl font-bold">Faixas de Preço: {product.name}</h1>
                <p className="text-muted-foreground">Gerencie as faixas de quantidade e valor unitário.</p>
            </div>

            <div className="flex justify-end mb-4">
                <PriceForm productId={id} />
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Qtd Mínima</TableHead>
                            <TableHead>Qtd Máxima</TableHead>
                            <TableHead>Preço Unitário</TableHead>
                            <TableHead className="text-right">Ações</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {product.prices.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                                    Nenhuma faixa de preço cadastrada.
                                </TableCell>
                            </TableRow>
                        )}
                        {product.prices.map((price) => (
                            <TableRow key={price.id}>
                                <TableCell>{price.minQuantity}</TableCell>
                                <TableCell>{price.maxQuantity}</TableCell>
                                <TableCell>
                                    {new Intl.NumberFormat("pt-BR", {
                                        style: "currency",
                                        currency: "BRL",
                                        minimumFractionDigits: 4,
                                    }).format(Number(price.unitPrice))}
                                </TableCell>
                                <TableCell className="text-right">
                                    <PriceActions price={price} productId={id} />
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
