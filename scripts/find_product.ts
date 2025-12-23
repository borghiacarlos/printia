import 'dotenv/config'
import { prisma } from '@/lib/prisma'

async function main() {
    const product = await prisma.product.findFirst({
        where: { name: 'Cartão de Visita' }
    })
    if (product) {
        console.log(`FOUND_PRODUCT_ID: ${product.id}`)
    } else {
        console.log('PRODUCT_NOT_FOUND')
    }
}

main()
