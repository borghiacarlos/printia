'use server'

import { z } from 'zod'
import { prisma } from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

const PriceSchema = z.object({
    id: z.string().optional(),
    productId: z.string().min(1, "Product ID required"),
    minQuantity: z.number().int().positive("Qtd Mínima deve ser positiva"),
    maxQuantity: z.number().int().positive("Qtd Máxima deve ser positiva"),
    unitPrice: z.number().positive("Preço deve ser positivo"),
}).refine(data => data.maxQuantity > data.minQuantity, {
    message: "Qtd Máxima deve ser maior que Mínima",
    path: ["maxQuantity"],
})

export type PriceFormData = z.infer<typeof PriceSchema>

async function checkOverlap(productId: string, min: number, max: number, excludeId?: string) {
    const existingprice = await prisma.priceTable.findFirst({
        where: {
            productId,
            id: excludeId ? { not: excludeId } : undefined,
            AND: [
                { minQuantity: { lte: max } },
                { maxQuantity: { gte: min } }
            ]
        }
    })
    return existingprice
}

export async function createPrice(data: PriceFormData) {
    const validated = PriceSchema.parse(data)

    const conflict = await checkOverlap(validated.productId, validated.minQuantity, validated.maxQuantity)

    if (conflict) {
        throw new Error(`Conflito de intervalo com faixa existente (Min: ${conflict.minQuantity}, Max: ${conflict.maxQuantity})`)
    }

    await prisma.priceTable.create({
        data: {
            productId: validated.productId,
            minQuantity: validated.minQuantity,
            maxQuantity: validated.maxQuantity,
            unitPrice: validated.unitPrice,
        },
    })

    revalidatePath(`/admin/produtos/${validated.productId}/precos`)
}

export async function updatePrice(data: PriceFormData) {
    if (!data.id) throw new Error("ID required for update")

    const validated = PriceSchema.parse(data)

    const conflict = await checkOverlap(validated.productId, validated.minQuantity, validated.maxQuantity, data.id)

    if (conflict) {
        throw new Error(`Conflito de intervalo com faixa existente (Min: ${conflict.minQuantity}, Max: ${conflict.maxQuantity})`)
    }

    await prisma.priceTable.update({
        where: { id: data.id },
        data: {
            minQuantity: validated.minQuantity,
            maxQuantity: validated.maxQuantity,
            unitPrice: validated.unitPrice,
        },
    })

    revalidatePath(`/admin/produtos/${validated.productId}/precos`)
}

export async function deletePrice(id: string, productId: string) {
    await prisma.priceTable.delete({
        where: { id },
    })
    revalidatePath(`/admin/produtos/${productId}/precos`)
}
