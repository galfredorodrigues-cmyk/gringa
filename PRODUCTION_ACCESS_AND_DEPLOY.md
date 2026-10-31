# HER POV — produção Hostinger + eventos Hotmart/Meta

**Fonte aprovada:** https://github.com/galfredorodrigues-cmyk/gringa (branch `main`).
**Site ao vivo:** https://vitrinyx.com/ (a hospedagem ainda deve receber a versão corrigida).
**Pixel Meta:** `1175307691488519`.

## O que o GitHub já entrega

- Node 20+ / Express / Nunjucks; `npm ci --ignore-scripts && npm test`; iniciar com `npm start`.
- `static/js/tracking.js`: PageView e ViewContent padronizados, somente após consentimento de marketing.
- Clique em checkout: evento customizado consentido `CheckoutLinkClick`, não confundir com padrão `InitiateCheckout`.
- `InitiateCheckout` deve vir da abertura real do checkout Hotmart; `Purchase` apenas após confirmação de pagamento pela Hotmart.
- Um pacote de produção sem tokens/variáveis de ambiente é gerado em GitHub Actions: `HER POV Hostinger production package`.
- Os testes Python do app Flask/Render são de legado. Não confundem a situação de venda da Hostinger, mas permanecem ativos como testes de regressão.

## Acesso seguro: limites

ChatGPT **não possui endereço de e-mail de colaborador próprio, conta Hostinger/Hotmart associada nem capacidade automática de aceitar convites**. Conceder acesso a um terceiro no painel não conecta esse terceiro a esta conversa. Para executar alterações pelo chat, é necessária uma integração/ferramenta efetivamente conectada com as permissões certas.

**Nunca envie no chat senhas, tokens, chaves API, códigos 2FA, links privados de sessão, assinatura eletrônica ou PDFs de compradores.**

### Hostinger — conectar GitHub diretamente ao site Node existente (preferido)

Abra https://hpanel.hostinger.com/ → Websites → `vitrinyx.com` → dashboard da aplicação Node → menu `...` → **Connect to GitHub** (ou reconectar). Autorize o GitHub e escolha exatamente `galfredorodrigues-cmyk/gringa`, branch `main`. Confira `Node.js 20/22`, entry `server.js`, comando `npm start` e as variáveis existentes; não sobrescreva valores válidos. A Hostinger pode fazer o redeploy no branch `main` quando a integração/auto-deploy estiver ativada. Só marque a implantação como concluída após **Deployments = Success** e inspeção do arquivo servido por `https://vitrinyx.com/static/js/tracking.js`.

Alternativa conservadora para app atualmente implantado por ZIP: no dashboard → Deployments → Redeploy → **Upload new files** e use o artifact da action `HER POV Hostinger production package` (um ZIP externo que contém o ZIP pronto). Não substitua ambiente nem código de outra aplicação.

Docs: https://www.hostinger.com/support/how-to-deploy-a-nodejs-website-in-hostinger/
Docs de redeploy: https://www.hostinger.com/support/how-to-redeploy-a-node-js-application/

### Hostinger — compartilhar conta com humano/organização de confiança

Dashboard → perfil → **Account Sharing** → **Give Access** → apenas o plano de hospedagem necessário → papel **Collaborator**, não Admin. Um colaborador real precisa informar e aceitar o convite por seu próprio e-mail; isto **não equivale a conceder acesso automaticamente ao ChatGPT**. O compartilhamento do plano pode abranger todos os sites nele hospedados.

Docs: https://www.hostinger.com/support/1583777-how-to-share-access-to-your-account-at-hostinger/

### Hotmart — conceder acesso limitado a colaborador real

Abra https://app.hotmart.com → **Parcerias → Gestão de Colaboradores → Perfis → Criar perfil**, conceda **Ferramentas: Gerenciamento de Pixel** e apenas as permissões adicionais necessárias. Depois **Cadastrar colaborador** com endereço real de um profissional/organização de confiança. A pessoa deve aceitar seu convite no próprio login; ChatGPT não tem e-mail para receber esse convite.

Docs: https://suportehotmart.zendesk.com/hc/pt-br/articles/115007885368-Como-configurar-e-acessar-a-Central-de-Colaboradores

### Hotmart — Meta Pixel por produto

Para cada produto de venda, vá a Ferramentas → Ver todas → Pixel de Rastreamento → Facebook + Instagram e informe `1175307691488519`. Habilite eventos **Visitas na página de pagamento** e **Vendas realizadas**. Configure Web e/ou API de Conversões conforme disponível e verifique deduplicação. Ao configurar eventos de pagamento não imediato, certifique-se de que `Purchase` conte apenas **pagamentos aprovados**, não boletos/Pix gerados.

Produtos registrados no projeto: 8805091, 8806705, 8806718, 8806725, 8808376; confira sua lista de produtos e ofertas antes de editar, incluindo as duas ofertas do bundle.

Docs: https://suportehotmart.zendesk.com/hc/pt-br/articles/115004826368-Como-configurar-o-Pixel-da-Meta-na-Hotmart
Opções avançadas: https://suportehotmart.zendesk.com/hc/pt-br/articles/6565866201741-Como-configuro-as-op%C3%A7%C3%B5es-avan%C3%A7adas-do-pixel-de-rastreamento-no-meu-produto

### Hotmart MCP

A Hotmart documenta um MCP com suporte a alguns dados/ações em clientes compatíveis, incluindo ChatGPT Desktop/Work. Isso não garante que o MCP possua a ação de **editar Pixel**, e ele não está conectado automaticamente a esta conversa. Não compartilhe as credenciais do MCP via chat.

Docs: https://suportehotmart.zendesk.com/hc/pt-br/articles/48741895558541-MCP-Hotmart-como-consultar-dados-e-realizar-a%C3%A7%C3%B5es-na-minha-conta-com-IA

## Critérios de liberação de anúncios

1. Deploys Hostinger mostram sucesso, `/health` está acessível e `tracking.js` servido contém os eventos novos.
2. Sem consentimento de marketing, não há requisições de Pixel; com consentimento, `PageView` + `ViewContent` aparecem corretamente em Test Events no Meta Events Manager.
3. Abrir o checkout Hotmart autorizado registra `InitiateCheckout` sem duplicação; não faça compra para testar sem autorização específica.
4. Com venda real aprovada e registrada pela Hotmart, validar exatamente um `Purchase` com valor, moeda e identificação adequados; deduplicar Web/CAPI.
5. Somente após esses passos reavaliar ativação da campanha e orçamento por conversões/ROAS; campanhas continuam pausadas até decisão consciente.
