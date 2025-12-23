'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { createPrice, updatePrice, PriceFormData } from '@/app/actions/prices'
import { Pencil } from 'lucide-react'

interface PriceFormProps {
    productId: string
    initialData?: PriceFormData & { id: string }
    trigger?: React.ReactNode
}

export function PriceForm({ productId, initialData, trigger }: PriceFormProps) {
    const [open, setOpen] = useState(false)
    const [error, setError] = useState<string | null>(null)

    async function handleSubmit(formData: FormData) {
        setError(null)
        const minQty = Number(formData.get('minQuantity'))
        const maxQty = Number(formData.get('maxQuantity'))
        const unitPrice = Number(formData.get('unitPrice'))

        // Basic Client Validation
        if (maxQty <= minQty) {
            setError("Quantidade Máxima deve ser maior que Mínima")
            return
        }

        const data = {
            id: initialData?.id,
            productId,
            minQuantity: minQty,
            maxQuantity: maxQty,
            unitPrice: unitPrice,
        }

        try {
            if (initialData) {
                await updatePrice(data)
            } else {
                await createPrice(data)
            }
            setOpen(false)
        } catch (e: any) {
            console.error(e)
            // Extract error message from server
            setError(e.message || "Erro ao salvar")
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                {trigger || <Button>Nova Faixa de Preço</Button>}
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{initialData ? 'Editar Faixa' : 'Nova Faixa de Preço'}</DialogTitle>
                </DialogHeader>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                        <span className="block sm:inline">{error}</span>
                    </div>
                )}

                <form action={handleSubmit} className="grid gap-4 py-4">
                    <input type="hidden" name="productId" value={productId} />

                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="minQuantity" className="text-right">Qtd Min</Label>
                        <Input id="minQuantity" name="minQuantity" type="number" defaultValue={initialData?.minQuantity} className="col-span-3" required />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="maxQuantity" className="text-right">Qtd Max</Label>
                        <Input id="maxQuantity" name="maxQuantity" type="number" defaultValue={initialData?.maxQuantity} className="col-span-3" required />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="unitPrice" className="text-right">Preço Unit</Label>
                        <Input id="unitPrice" name="unitPrice" type="number" step="0.0001" defaultValue={initialData?.unitPrice} className="col-span-3" required />
                    </div>

                    <div className="flex justify-end mt-4">
                        <Button type="submit">{initialData ? 'Salvar Alterações' : 'Adicionar Faixa'}</Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    )
}
