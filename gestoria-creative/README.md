# Gestoría Creative · Guía del programa

Documento para enseñar Gestoría Creative a las asesorías y gestorías: cada sección del programa con capturas reales
y tres bloques, **Qué hace**, **Qué ves** y **Qué genera**. Edición de octubre de 2026.

| Qué | Dónde |
|---|---|
| Guía en PDF (A4, 89 páginas) para enviar o imprimir | [`Gestoria-Creative-Guia-del-programa.pdf`](Gestoria-Creative-Guia-del-programa.pdf) |
| Guía web (se abre en el navegador; las capturas se amplían al pulsarlas) | [`guia/index.html`](guia/index.html) |
| Logos de Gestoría Creative en SVG y PNG | [`marca/`](marca/) |
| Textos y generador de la guía | [`fuente/`](fuente/) |

## Contenido

- Portada, qué es el programa y cómo encaja todo (lo que entra, lo que hace y lo que sale).
- 34 secciones en el orden del menú: Inicio y clientes, Trabajo diario, Contabilidad, Despacho y Portal del cliente.
- Anexos: todo lo que genera el programa (ficheros, avisos y registros), seguridad y protección de datos, e
  instalación y requisitos.

Las capturas son de la instalación de demostración (40 clientes ficticios de «Asesoría Ejemplo»). Nombres, NIF,
importes y actos del BORME son inventados. Los textos describen solo lo que el programa hace hoy; lo que aún está en
desarrollo (por ejemplo, los libros contables con pantalla propia, la facturación de honorarios o el módulo de
cumplimiento) no aparece como función.

## Marca

- Icono: la G naranja en degradado con el punto turquesa sobre fondo `#12161C`.
- Logotipo: «GESTORÍA» en blanco (o `#12161C` sobre fondo claro) y «CREATIVE» en naranja `#F8841A`, en Montserrat
  Black, igual que el logotipo de Webs Creative. El texto está convertido a trazos, así que no hace falta la fuente.
- Colores: naranja `#F8841A`, negro tinta `#12161C` y turquesa `#22D3EE`.

## Cambiar los textos

Los textos de cada grupo están en `fuente/contenido/*.json` y la portada, la presentación, los anexos y el cierre en
`fuente/extra.json`. `fuente/build.py` genera el HTML con `styles.css` y `fuente/montar.py` junta los grupos y
convierte las capturas. Para regenerar la guía completa hacen falta las capturas originales en PNG, que se sacan de
la instalación de demostración.
