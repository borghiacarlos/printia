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
import { createMaterial, updateMaterial, MaterialFormData } from '@/app/actions/materials'

interface MaterialDialogProps {
    children?: React.ReactNode
    material?: MaterialFormData & { id: string }
}

export function MaterialDialog({ children, material }: MaterialDialogProps) {
    const [open, setOpen] = useState(false)

    async function handleSubmit(formData: FormData) {
        const data = {
            id: material?.id,
            name: formData.get('name') as string,
            brand: formData.get('brand') as string,
            format: formData.get('format') as string,
            grammage: Number(formData.get('grammage')),
            packetCost: Number(formData.get('packetCost')),
            packetQty: Number(formData.get('packetQty')),
        }

        try {
            if (material) {
                await updateMaterial(data)
            } else {
                await createMaterial(data)
            }
            setOpen(false)
        } catch (error) {
            console.error(error)
            alert("Erro ao salvar material. Verifique os dados.")
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                {children || <Button>Novo Material</Button>}
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{material ? 'Editar Material' : 'Novo Material'}</DialogTitle>
                </DialogHeader>
                <form action={handleSubmit} className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="name" className="text-right">Nome</Label>
                        <Input id="name" name="name" defaultValue={material?.name} className="col-span-3" required />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="brand" className="text-right">Marca</Label>
                        <Input id="brand" name="brand" defaultValue={material?.brand} className="col-span-3" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="format" className="text-right">Formato</Label>
                        <Input id="format" name="format" defaultValue={material?.format} placeholder="ex: A3, SRA3" className="col-span-3" required />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="grammage" className="text-right">Gramatura</Label>
                        <Input id="grammage" name="grammage" type="number" defaultValue={material?.grammage} className="col-span-3" required />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="packetCost" className="text-right">Custo Pct (R$)</Label>
                        <Input id="packetCost" name="packetCost" type="number" step="0.01" defaultValue={material?.packetCost} className="col-span-3" required />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="packetQty" className="text-right">Qtd Folhas</Label>
                        <Input id="packetQty" name="packetQty" type="number" defaultValue={material?.packetQty} className="col-span-3" required />
                    </div>

                    <div className="flex justify-end mt-4">
                        <Button type="submit">{material ? 'Salvar Alterações' : 'Criar Material'}</Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    )
}
