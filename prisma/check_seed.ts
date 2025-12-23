import { PrismaClient } from '../lib/generated/prisma/client'

const prisma = new PrismaClient()

async function main() {
    const printers = await prisma.printer.findMany({ include: { supplies: true } })
    const papers = await prisma.paperStock.findMany()
    const products = await prisma.product.findMany({ include: { prices: true } })
    const finishings = await prisma.finishing.findMany()

    console.log('--- Verification Report ---')
    console.log(`Printers count: ${printers.length}`)
    if (printers.length > 0) {
        console.log(`Printer 1: ${printers[0].name} (Supplies: ${printers[0].supplies.length})`)
    }

    console.log(`Papers count: ${papers.length}`)
    if (papers.length > 0) {
        console.log(`Paper 1: ${papers[0].name}`)
    }

    console.log(`Products count: ${products.length}`)
    console.log(`Finishings count: ${finishings.length}`)
}

main()
    .then(async () => {
        await prisma.$disconnect()
    })
    .catch(async (e) => {
        console.error(e)
        await prisma.$disconnect()
        process.exit(1)
    })
