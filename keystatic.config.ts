import { config, fields, collection, singleton } from '@keystatic/core';

const status = () => fields.select({
  label: 'Publication status',
  description: 'Keep unfinished content as a draft. Published entries appear when the site is rebuilt.',
  options: [{ label: 'Draft — hidden from visitors', value: 'draft' }, { label: 'Published', value: 'published' }],
  defaultValue: 'draft',
});
const photo = (label = 'Photo') => fields.image({ label, directory: 'public/images/uploads', publicPath: '/images/uploads/' });
const text = (label: string, description?: string) => fields.text({ label, description, validation: { isRequired: true } });

export default config({
  storage: { kind: 'local' },
  ui: { brand: { name: 'Critter Creek · Content Studio' }, navigation: {
    'Your website': ['homepage', 'settings', 'pages'],
    'Life at the ranch': ['animals', 'events'],
  } },
  singletons: {
    homepage: singleton({
      label: 'Homepage', path: 'src/content/homepage', format: { data: 'json' },
      schema: {
        eyebrow: text('Small introductory line'),
        headline: fields.text({label:'Main headline', description:'Put the second part on a new line for the red italic treatment.', multiline:true, validation:{isRequired:true}}),
        farmSlides: fields.array(fields.object({
          photo: photo('Slideshow photo'),
          alt: text('Photo description', 'Describe the animals and the scene for someone who cannot see the photo.'),
          caption: text('Short caption'),
          focus: fields.select({ label: 'Photo focus', description: 'Choose which part of the photo stays visible in the wide slideshow. Review on a phone too.', options: [ {label:'Top', value:'top'}, {label:'Upper middle', value:'upper'}, {label:'Center', value:'center'}, {label:'Lower middle', value:'lower'}, {label:'Bottom', value:'bottom'} ], defaultValue:'center' }),
        }), { label: 'Farm homepage slideshow', description: 'Photos shown on the selected Farm Journal homepage. Drag to change their order.', itemLabel: props => props.fields.caption.value || 'New slideshow photo' }),
      },
    }),
    settings: singleton({
      label: 'Contact & links', path: 'src/content/settings', format: { data: 'json' },
      schema: {
        name: text('Organization name'), email: text('Contact email'), phone: text('Telephone'), address: text('Street address'), city: text('City, state & ZIP'),
        donationUrl: fields.url({ label: 'Approved donation page', description: 'Leave empty until the ranch confirms the payment destination. The site will offer phone/email contact instead.' }),
        volunteerUrl: fields.url({ label: 'Volunteer application link' }),
        waiverUrl: fields.url({ label: 'Visitor waiver link' }),
      },
    }),
  },
  collections: {
    animals: collection({
      label: 'Animals', slugField: 'name', path: 'src/content/animals/*', format: { data: 'json' },
      columns: ['name', 'species', 'status'],
      schema: {
        name: fields.slug({ name: { label: 'Name or descriptive title', validation: { isRequired: true } } }),
        species: text('Animal type'), status: status(),
        order: fields.integer({ label: 'Display order', defaultValue: 10, validation: { min: 0 } }),
        photo: photo(), alt: text('Photo description'),
        introduction: fields.text({ label: 'Short introduction', multiline: true, validation: { isRequired: true } }),
        story: fields.text({ label: 'Their story', description: 'Separate paragraphs with an empty line. Use only confirmed information.', multiline: true }),
        care: fields.text({ label: 'How your support helps', multiline: true }),
      },
    }),
    events: collection({
      label: 'Events', slugField: 'title', path: 'src/content/events/*', format: { data: 'json' },
      columns: ['title', 'date', 'status'],
      schema: {
        title: fields.slug({ name: { label: 'Event title', validation: { isRequired: true } } }),
        status: status(), date: fields.date({ label: 'Event date', validation: { isRequired: true } }),
        time: text('Time', 'Include the time zone, e.g. 10 am–noon Eastern.'),
        location: text('Location'),
        category: fields.select({ label: 'Event type', options: [ { label: 'Visit', value: 'visit' }, { label: 'Education', value: 'education' }, { label: 'Volunteer', value: 'volunteer' }, { label: 'Fundraiser', value: 'support' } ], defaultValue: 'visit' }),
        photo: photo(), alt: fields.text({ label: 'Photo description' }),
        summary: fields.text({ label: 'Short summary', multiline: true, validation: { isRequired: true } }),
        details: fields.text({ label: 'Full details', multiline: true }),
        registrationUrl: fields.url({ label: 'Registration link', description: 'Optional. Without a link, visitors are invited to email the ranch.' }),
      },
    }),
    pages: collection({
      label: 'Pages', slugField: 'title', path: 'src/content/pages/*', format: { data: 'json' },
      columns: ['title', 'status'],
      schema: {
        title: fields.slug({ name: { label: 'Page title', validation: { isRequired: true } } }),
        status: status(), eyebrow: text('Small introductory line'), headline: text('Page headline'),
        introduction: fields.text({ label: 'Introduction', multiline: true, validation: { isRequired: true } }),
        photo: photo(), alt: text('Photo description'),
        sections: fields.array(fields.object({ heading: text('Heading'), body: fields.text({ label: 'Text', multiline: true, validation: { isRequired: true } }) }), { label: 'Page sections', itemLabel: props => props.fields.heading.value || 'New section' }),
        ctaLabel: text('Button label'),
        ctaSubject: text('Email inquiry subject'),
      },
    }),
  },
});
