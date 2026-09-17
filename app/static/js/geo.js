/**
 * Script de integração GeoAPI.pt para autocompletar moradas
 * Acoplamento via classes/ids de form
 */

document.addEventListener('DOMContentLoaded', () => {
    const cpInput = document.getElementById('codigo_postal');
    const btnBusca = document.getElementById('btn_busca_cp');
    const localidadeInput = document.getElementById('localidade');
    const concelhoInput = document.getElementById('concelho');
    const distritoInput = document.getElementById('distrito');

    if (!cpInput) return; // Não há campo de CP na tela atual

    const buscarMoradaGeoAPI = async () => {
        let cp = cpInput.value.replace(/\D/g, '');
        if (cp.length !== 7) return;

        // Feedback visual
        if (btnBusca) {
            btnBusca.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        }

        try {
            const cepFormatado = cp.substring(0,4) + '-' + cp.substring(4);
            const response = await fetch(`/configuracoes/api/geo/codigo-postal/${cepFormatado}`);
            
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success' && data.dados && data.dados.length > 0) {
                    const info = data.dados[0];
                    
                    if (localidadeInput) localidadeInput.value = info.Localidade || '';
                    if (concelhoInput) concelhoInput.value = info.Concelho || '';
                    if (distritoInput) distritoInput.value = info.Distrito || '';
                } else if (data.status === 'success' && data.dados && typeof data.dados === 'object' && !Array.isArray(data.dados)) {
                    // Trata também objeto único se a API vier diferente
                     if (localidadeInput) localidadeInput.value = data.dados.Localidade || '';
                     if (concelhoInput) concelhoInput.value = data.dados.Concelho || '';
                     if (distritoInput) distritoInput.value = data.dados.Distrito || '';
                }
            } else {
                console.warn('GeoAPI desativada ou não respondeu via backend proxy', await response.text());
            }
        } catch (err) {
            console.error('Erro na conexão com API interna GeoAPI', err);
        } finally {
            if (btnBusca) {
                btnBusca.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i>';
            }
        }
    };

    // Formatação de máscara visual
    cpInput.addEventListener('input', (e) => {
        let x = e.target.value.replace(/\D/g, '').match(/(\d{0,4})(\d{0,3})/);
        e.target.value = !x[2] ? x[1] : x[1] + '-' + x[2];
    });

    // Dispara busca quando o usuário sai do campo
    cpInput.addEventListener('blur', buscarMoradaGeoAPI);

    // Dispara busca com o botão (se existir)
    if (btnBusca) {
        btnBusca.addEventListener('click', (e) => {
            e.preventDefault();
            buscarMoradaGeoAPI();
        });
    }
});