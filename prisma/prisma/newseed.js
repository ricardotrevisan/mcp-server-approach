const { PrismaClient } = require('@prisma/client');
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

function generateCity(index) {
  return index % 2 === 0 ? "São Paulo" : "Rio de Janeiro";
}

function generateState(index) {
  return index % 2 === 0 ? "SP" : "RJ";
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

async function main() {
  for (let i = 1; i <= 50; i++) {
    const debtor = await prisma.debtor.upsert({
      where: { cpf: generateCpf(i) },
      update: {},
      create: {
        cpf: generateCpf(i),
        phone: generatePhone(i),
        email: generateEmail(i),
        full_name: generateName(i),
        birth_date: `1980-01-${String((i % 28) + 1).padStart(2, '0')}`,
        mother_name: `Mãe Teste ${i}`,
        verified: i % 2 === 0,
        authorized: i % 2 === 0,
        trust_level: (i % 5) + 1,
        score: randomInt(0, 100),

        // Perfis
        profiles: {
          create: Array.from({ length: randomInt(1, 3) }, (_, idx) => ({
            phone: generatePhone(i + idx),
            email: `profile${idx}_${generateEmail(i)}`,
            city: generateCity(i + idx),
            state: generateState(i + idx),
            postal_code: `0100${String(i + idx).padStart(2, '0')}-000`,
            active: idx % 2 === 0,
          })),
        },

        // Logs de acesso com exceptions
        access_logs: {
          create: Array.from({ length: randomInt(1, 3) }, (_, logIdx) => ({
            token: `token-${i}-${logIdx}`,
            ip_address: `192.168.${i}.${logIdx}`,
            device_id: `device-${i}-${logIdx}`,
            utm_campaign: "campanha-teste",
            utm_source: "source-teste",
            exceptions: {
              create: Array.from({ length: randomInt(0, 2) }, (_, exIdx) => ({
                category: "erro_login",
                cpf: generateCpf(i),
                full_name: generateName(i),
                phone: generatePhone(i),
                email: generateEmail(i),
                cpf_attempt: generateCpf(i + 100 + exIdx),
                full_name_attempt: `Tentativa ${i}-${exIdx}`,
                birth_date_attempt: `1980-02-${String((i % 28) + 1).padStart(2, '0')}`,
                phone_attempt: `1199${String(200000 + i + exIdx).slice(-8)}`,
                email_attempt: `tentativa${i}-${exIdx}@teste.com`,
              })),
            },
          })),
        },

        // Tokens SMS
        sms_tokens: {
          create: Array.from({ length: randomInt(1, 2) }, (_, idx) => ({
            token: `sms-token-${i}-${idx}`,
            phone: generatePhone(i + idx),
            subject: "Teste SMS",
            message: "Mensagem de teste",
          })),
        },

        // Enriquecimento de dados
        data_enrichments: {
          create: Array.from({ length: randomInt(1, 2) }, (_, idx) => ({
            token: `enrichment-${i}-${idx}`,
            result: "OK",
            summary: "Resumo de teste",
          })),
        },

        // Agreements e Proposals
        agreements: {
          create: Array.from({ length: randomInt(0, 3) }, (_, agrIdx) => ({
            contract: `Contrato ${i}-${agrIdx}`,
            error: "",
            agreement_number: `${10000 + i + agrIdx}`,
            status: agrIdx % 2 === 0,
            total_discount: 50 + i + agrIdx,
            proposals: {
              create: Array.from({ length: randomInt(0, 3) }, (_, propIdx) => {
                const totalValue = 1000 + i * 10 + propIdx * 100;
                const installments = randomInt(1, 6);
                return {
                  total_installments: installments,
                  total_value: totalValue,
                  installment_value: totalValue / installments,
                  total_discount: 50 + propIdx,
                  original_balance: totalValue + 100,
                };
              }),
            },
          })),
        },
      },
      include: {
        profiles: true,
        access_logs: { include: { exceptions: true } },
        sms_tokens: true,
        data_enrichments: true,
        agreements: { include: { proposals: true } },
      },
    });

    console.log(`Debtor ${i} criado/atualizado: ${debtor.cpf}`);
  }
}

main()
  .catch((e) => console.error(e))
  .finally(async () => {
    await prisma.$disconnect();
  });
