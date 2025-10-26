import markdown
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect
from core.services import gemini


def index_ask(request):
    # Inicializar historial de conversación
    if 'historial' not in request.session:
        request.session['historial'] = []

    historial = request.session['historial']

    if request.method == "POST":
        valor = request.POST.get("campo")

        # Si presiona el botón de borrar
        if 'borrar' in request.POST:
            request.session['historial'] = []
            request.session.modified = True
            return redirect('vista')

        # Guarda el mensaje del usuario
        historial.append({
            'rol': 'usuario',
            'mensaje': valor
        })

        # Respuesta de LexRevoX (texto plano con formato Markdown)
        respuesta = gemini.generate_augmented_response(valor, historial)

        # Guarda la respuesta (sin procesar aún)
        historial.append({
            'rol': 'lexrevox',
            'mensaje': respuesta  # ← Se guarda en texto Markdown
        })

        # Guarda los cambios en sesión
        request.session.modified = True

    # --- Convertir mensajes Markdown a HTML SOLO al renderizar ---
    historial_html = []
    for mensaje in historial:
        if mensaje['rol'] == 'lexrevox':
            contenido_html = mark_safe(
                markdown.markdown(mensaje['mensaje'], extensions=['extra', 'sane_lists'])
            )
        else:
            contenido_html = mensaje['mensaje']
        historial_html.append({
            'rol': mensaje['rol'],
            'mensaje': contenido_html
        })

    return render(request, "core/index_ask.html", {'historial': historial_html})
