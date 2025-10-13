const { PrismaClient, Prisma } = require('@prisma/client');
const prisma = new PrismaClient();

function generateCpf(index) {
  return (10000000000 + index).toString();
}

function generateName(index) {
  return `Usuário Teste ${index}`;
}

function generateEmail(index) {
  return `teste${index}@teste.com`;
}

function generatePhone(index) {
  return `1199${String(100000 + index).slice(-8)}`;
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

async function main() {
  console.log('🧩 Iniciando seed...');

  // 1️⃣ Criação das estratégias e regras
  const maximizeRecovery = await prisma.negotiationStrategy.upsert({
    where: { name: 'maximize_recovery' },
    update: {},
    create: {
      name: 'maximize_recovery',
      description: 'Maximize recovery for mid-range balances',
      rules: {
        create: [
          {
            min_value: new Prisma.Decimal('0.01'),
            max_value: new Prisma.Decimal('1000'),
            max_installments: 4,
            max_discount_percent: 25,
            min_downpayment_percent: 30,
            valid_until: new Date('2025-12-31T00:00:00Z'),
          },
          {
            min_value: new Prisma.Decimal('1000.01'),
            max_value: new Prisma.Decimal('5000'),
            max_installments: 12,
            max_discount_percent: 15,
            min_downpayment_percent: 20,
            valid_until: new Date('2025-12-31T00:00:00Z'),
          },
          {
            min_value: new Prisma.Decimal('5000.01'),
            max_value: new Prisma.Decimal('10000'),
            max_installments: 18,
            max_discount_percent: 15,
            min_downpayment_percent: 10,
            valid_until: new Date('2025-12-31T00:00:00Z'),
          },
          {
            min_value: new Prisma.Decimal('10000.01'),
            max_value: new Prisma.Decimal('999999.99'),
            max_installments: 36,
            max_discount_percent: 5,
            min_downpayment_percent: 10,
            valid_until: new Date('2025-12-31T00:00:00Z'),
          },
        ],
      },
    },
  });

  const loyalCustomer = await prisma.negotiationStrategy.upsert({
    where: { name: 'loyal_customer' },
    update: {},
    create: {
      name: 'loyal_customer',
      description: 'Preferential terms for loyal customers',
      rules: {
        create: [
          {
            min_value: new Prisma.Decimal('0.01'),
            max_value: new Prisma.Decimal('1000'),
            max_installments: 6,
            max_discount_percent: 30,
            min_downpayment_percent: 20,
            valid_until: new Date('2025-12-31T00:00:00Z'),
          },
          {
            min_value: new Prisma.Decimal('1000.01'),
            max_value: new Prisma.Decimal('5000'),
            max_installments: 18,
            max_discount_percent: 20,
            min_downpayment_percent: 10,
            valid_until: new Date('2025-12-31T00:00:00Z'),
          },
          {
            min_value: new Prisma.Decimal('5000.01'),
            max_value: new Prisma.Decimal('999999.99'),
            max_installments: 24,
            max_discount_percent: 15,
            min_downpayment_percent: 10,
            valid_until: new Date('2025-12-31T00:00:00Z'),
          },
        ],
      },
    },
  });

  console.log('✅ Estratégias e regras criadas.');

  // 2️⃣ Criação de devedores + contratos + acordos
  for (let i = 1; i <= 50; i++) {
    const trustLevel = (i % 5) + 1;
    const assignedStrategyId = trustLevel >= 4 ? loyalCustomer.id : maximizeRecovery.id;

    const debtor = await prisma.debtor.upsert({
      where: { cpf: generateCpf(i) },
      update: {
        phone: generatePhone(i),
        email: generateEmail(i),
        full_name: generateName(i),
      },
      create: {
        cpf: generateCpf(i),
        phone: generatePhone(i),
        email: generateEmail(i),
        full_name: generateName(i),
        birth_date: `1980-01-${String((i % 28) + 1).padStart(2, '0')}`,
        mother_name: `Mãe Teste ${i}`,
        verified: i % 2 === 0,
        authorized: i % 2 === 0,
        trust_level: trustLevel,
        score: randomInt(0, 100),
      },
    });

    console.log(`👤 Devedor criado/atualizado: ${debtor.full_name}`);

    // Cria de 1 a 3 contratos
    const contractsCount = randomInt(1, 3);
    for (let c = 0; c < contractsCount; c++) {
      const totalValue = 500 + i * 5 + c * 50;

      await prisma.engageableContract.create({
        data: {
          debtor_id: debtor.id,
          strategy_id: assignedStrategyId,
          total_value: totalValue,
          original_balance: totalValue + 50,
          age: randomInt(0, 365),
          status: true,
        },
      });
    }

    // Cria de 0 a 2 acordos simulados
    const agreementsCount = randomInt(0, 2);
    for (let k = 0; k < agreementsCount; k++) {
      const totalValue = 1000 + i * 10 + k * 50;
      const installments = randomInt(1, 6);

      await prisma.agreement.create({
        data: {
          debtor_id: debtor.id,
          agreement_number: `${10000 + i + k}`,
          status: true,
          total_value: totalValue,
          original_balance: totalValue + 100,
          installments,
          total_discount: new Prisma.Decimal(randomInt(5, 50)),
          first_payment_date: new Date(2025, 9, randomInt(1, 28)),
        },
      });
    }
  }

  console.log('✅ Devedores, contratos e acordos criados.');
}

main()
  .catch((e) => {
    console.error('❌ Erro ao executar seed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
    console.log('🏁 Seed finalizado.');
  });
