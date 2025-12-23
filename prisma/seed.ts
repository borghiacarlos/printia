import { PrismaClient } from '../lib/generated/prisma/client'

const prisma = new PrismaClient()

async function main() {
    console.log('🌱 Starting seed...')

    // 1. Create Printer: Konica Minolta 2060
    const printer = await prisma.printer.create({
        data: {
            name: 'Konica Minolta 2060',
            currentCounter: 150000,
            supplies: {
                create: [
                    {
                        itemName: 'Toner Preto TN-619K',
                        cost: 450.00,
                        startCounter: 145000,
                        installedAt: new Date('2024-01-15'),
                    },
                    {
                        itemName: 'Toner Ciano TN-619C',
                        cost: 520.00,
                        startCounter: 148000,
                        installedAt: new Date('2024-02-01'),
                    }
                ]
            }
        }
    })
    console.log(`✅ Created printer: ${printer.name}`)

    // 2. Create PaperStock: Couchê 170g
    const paper = await prisma.paperStock.create({
        data: {
            name: 'Couchê Fosco 170g',
            brand: 'Suzano',
            grammage: 170,
            format: 'SRA3',
            packetCost: 55.90,
            packetQty: 250,
            unitCost: 55.90 / 250, // 0.2236
        }
    })
    console.log(`✅ Created paper: ${paper.name}`)

    // 3. Create Example Product (Optional context)
    const product = await prisma.product.create({
        data: {
            name: 'Cartão de Visita',
            category: 'Corporativo',
            description: 'Cartão de visita padrão 9x5cm',
            prices: {
                create: [
                    {
                        minQuantity: 100,
                        maxQuantity: 499,
                        unitPrice: 0.45
                    },
                    {
                        minQuantity: 500,
                        maxQuantity: 999,
                        unitPrice: 0.35
                    }
                ]
            }
        }
    })
    console.log(`✅ Created product: ${product.name}`)

    // 4. Create Finishing (Optional context)
    const finishing = await prisma.finishing.create({
        data: {
            name: 'Laminação Fosca Frente',
            priceFixed: 15.00, // Setup
            pricePerUnit: 0.15, // Cost per sheet side
            isActive: true
        }
    })
    console.log(`✅ Created finishing: ${finishing.name}`)
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
