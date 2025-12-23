'use client'

import { Trash, Pencil } from "lucide-react"
import { Button } from "@/components/ui/button"
import { deletePrice } from "@/app/actions/prices"
import { PriceForm } from "./price-form"

interface PriceActionsProps {
    price: any
    productId: string
}

export function PriceActions({ price, productId }: PriceActionsProps) {
    return (
        <div className="flex items-center gap-2 justify-end">
            <PriceForm
                productId={productId}
                initialData={price}
                trigger={
                    <Button variant="ghost" size="icon">
                        <Pencil className="h-4 w-4" />
                    </Button>
                }
            />

            <Button
                variant="ghost"
                size="icon"
                className="text-red-500 hover:text-red-700"
                onClick={async () => {
                    if (confirm("Excluir esta faixa de preço?")) {
                        await deletePrice(price.id, productId)
                    }
                }}
            >
                <Trash className="h-4 w-4" />
            </Button>
        </div>
    )
}
