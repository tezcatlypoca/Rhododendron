import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OrchestreFormComponent } from './orchestre-form.component';

describe('OrchestreFormComponent', () => {
  let component: OrchestreFormComponent;
  let fixture: ComponentFixture<OrchestreFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrchestreFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OrchestreFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
