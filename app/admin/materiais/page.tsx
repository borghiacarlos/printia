import { prisma } from "@/lib/prisma";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { MaterialDialog } from "./components/material-dialog";
import { MaterialActions } from "./components/material-actions";

export default async function MateriaisPage() {
    const materials = await prisma.paperStock.findMany({
        orderBy: { createdAt: "desc" },
    });

    return (
        <div className="container mx-auto py-10">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Gerenciar Materiais (Papéis)</h1>
                <MaterialDialog />
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Nome</TableHead>
                            <TableHead>Marca</TableHead>
                            <TableHead>Gramatura</TableHead>
                            <TableHead>Formato</TableHead>
                            <TableHead>Custo Pct</TableHead>
                            <TableHead>Qtd Folhas</TableHead>
                            <TableHead className="font-bold text-green-600">
                                Custo Unit (Calc)
                            </TableHead>
                            <TableHead className="text-right">Ações</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {materials.map((material) => (
                            <TableRow key={material.id}>
                                <TableCell className="font-medium">{material.name}</TableCell>
                                <TableCell>{material.brand}</TableCell>
                                <TableCell>{material.grammage}g</TableCell>
                                <TableCell>{material.format}</TableCell>
                                <TableCell>
                                    {new Intl.NumberFormat("pt-BR", {
                                        style: "currency",
                                        currency: "BRL",
                                    }).format(Number(material.packetCost))}
                                </TableCell>
                                <TableCell>{material.packetQty}</TableCell>
                                <TableCell className="font-bold text-green-700">
                                    {/* Fallback calculation if unitCost is null, though we set it */}
                                    {new Intl.NumberFormat("pt-BR", {
                                        style: "currency",
                                        currency: "BRL",
                                        minimumFractionDigits: 4,
                                    }).format(Number(material.unitCost) || (Number(material.packetCost) / material.packetQty))}
                                </TableCell>
                                <TableCell className="text-right">
                                    <MaterialActions material={material} />
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
