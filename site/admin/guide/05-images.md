# Photos and images

## Adding a photo Kate gives you

1. **Ask who took it** and whether it may be published. No credit, no publishing.
2. **Remove the hidden metadata** (location, camera, date) and make web sizes:

        python3 - <<'PY'
        from PIL import Image
        im = Image.open('INPUT.jpg'); im = im.convert('RGB')
        im.save('site/img/NAME.webp', 'WEBP', quality=82)          # full size, metadata removed
        w = 640; h = int(im.height * w / im.width)
        im.resize((w, h)).save('site/img/NAME-640.webp', 'WEBP', quality=80)
        PY

3. **Use it with a srcset**, width and height, and a real description in alt (what the photo shows, for someone who cannot see it).
4. **Credit it** next to the photo and in the footer, as the desk photo is credited ("Photo by Matt Hinton Photography").
5. **Log the source** in docs/sources.md: file, who took it, what Kate said about permission, date.

## Images that need Kate's yes first

The LinkedIn banner headshot (photographer not yet known), the Audio Genius logo, and the "Audio Genius needs you" poster are in material/ but not yet cleared. Ask Kate the questions in docs/questions-for-kate.md first.

## Never

A photo of anyone other than Kate without their consent; a logo or image Kate does not have the right to use; generated images presented as real photos.

## The share card

site/img/share-card.jpg (1200 x 630) is the picture shown when the site is shared on WhatsApp, LinkedIn or X. If the hero photo or Kate's headline changes, make a new one the same size, under 300 KB, with the credit on it.
