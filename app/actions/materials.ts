'use server'

import { z } from 'zod'
import { prisma } from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

// Schema Validation
const MaterialSchema = z.object({
    id: z.string().optional(),
    name: z.string().min(1, "Nome é obrigatório"),
    brand: z.string().optional(),
    grammage: z.number().int().positive("Gramatura deve ser positiva"),
    format: z.string().min(1, "Formato é obrigatório"),
    packetCost: z.number().positive("Custo do pacote deve ser positivo"),
    packetQty: z.number().int().positive("Quantidade deve ser positiva"),
})

export type MaterialFormData = z.infer<typeof MaterialSchema>

export async function createMaterial(data: MaterialFormData) {
    const validated = MaterialSchema.parse(data)

    // Calculate unit cost automatically
    const unitCost = validated.packetCost / validated.packetQty

    await prisma.paperStock.create({
        data: {
            name: validated.name,
            brand: validated.brand,
            grammage: validated.grammage,
            format: validated.format,
            packetCost: validated.packetCost,
            packetQty: validated.packetQty,
            unitCost: unitCost,
        },
    })

    revalidatePath('/admin/materiais')
}

export async function updateMaterial(data: MaterialFormData) {
    if (!data.id) throw new Error("ID is required for update")

    const validated = MaterialSchema.parse(data)

    // Recalculate unit cost
    const unitCost = validated.packetCost / validated.packetQty

    await prisma.paperStock.update({
        where: { id: data.id },
        data: {
            name: validated.name,
            brand: validated.brand,
            grammage: validated.grammage,
            format: validated.format,
            packetCost: validated.packetCost,
            packetQty: validated.packetQty,
            unitCost: unitCost,
        },
    })

    revalidatePath('/admin/materiais')
}

export async function deleteMaterial(id: string) {
    await prisma.paperStock.delete({
        where: { id },
    })

    revalidatePath('/admin/materiais')
}
