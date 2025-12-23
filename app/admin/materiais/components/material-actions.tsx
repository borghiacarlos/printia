'use client'

import { MoreHorizontal, Pencil, Trash } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { deleteMaterial } from "@/app/actions/materials"
import { MaterialDialog } from "./material-dialog"

export function MaterialActions({ material }: { material: any }) {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                    <span className="sr-only">Open menu</span>
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuLabel>Ações</DropdownMenuLabel>

                {/* Edit Action - Wraps the MenuItem in Dialog Trigger logic implicitly via composition or we need a cleaner way. 
            Since Dialog cannot be easily inside DropdownItem without closing issues, we use a trick or just open dialog from here.
            Actually, shadcn/ui DropdownMenu closes on click. 
            Best UX: Put the Edit Button OUTSIDE or handle state carefully. 
            Simple approach: Use the Dialog as a controlled component or wrapping the trigger.
            Here we wrap the "Editar" text/button with the MaterialDialog, but MaterialDialog expects a trigger.
        */}

                <div onSelect={(e) => e.preventDefault()}>
                    <MaterialDialog material={material}>
                        <div className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50">
                            <Pencil className="mr-2 h-4 w-4" />
                            Editar
                        </div>
                    </MaterialDialog>
                </div>

                <DropdownMenuItem
                    className="text-red-600 focus:text-red-600"
                    onClick={async () => {
                        if (confirm('Tem certeza que deseja excluir?')) {
                            await deleteMaterial(material.id)
                        }
                    }}
                >
                    <Trash className="mr-2 h-4 w-4" />
                    Excluir
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
